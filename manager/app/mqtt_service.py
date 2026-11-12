"""MQTT connectivity, last display message and sensor node state for the display manager."""
import json
import logging
import threading

import paho.mqtt.client as mqtt

from .sensor_store import SensorStore


class MqttService:
    """Wraps the paho MQTT client, tracking the most recent display message and sensor nodes."""

    def __init__(self, config, sensor_store=None):
        self.config = config
        self.sensor_store = sensor_store or SensorStore()
        self._handlers = {}  # subscription -> fn(topic, payload_bytes)
        # Broker's answer to each subscription: "pending", "ok" or "refused". A refused one
        # (e.g. the account isn't authorised for it) otherwise looks like silence.
        self.subscription_status = {}
        self._pending_subs = {}  # SUBSCRIBE message id -> subscription
        self.last_message = {
            "topic": None,
            "payload": None,
            "layout": None,
            "widgets": None,
            "version": 0,
        }
        self.message_event = threading.Event()

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=config.MQTT_CLIENT_ID)
        self.client.username_pw_set(username=config.MQTT_USER, password=config.MQTT_PASSWD)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe

    def _on_connect(self, client, userdata, flags, rc, properties):
        logging.info("MQTT connected: %s", mqtt.connack_string(rc))
        if rc == 0:
            self._subscribe(self.config.MQTT_TOPIC)
            self._subscribe(self.config.SENSOR_TOPIC)
            for subscription in self._handlers:
                self._subscribe(subscription)

    def _subscribe(self, subscription):
        self.subscription_status[subscription] = "pending"
        result, mid = self.client.subscribe(subscription)
        if result == mqtt.MQTT_ERR_SUCCESS:
            self._pending_subs[mid] = subscription

    def _on_subscribe(self, client, userdata, mid, reason_codes, properties):
        subscription = self._pending_subs.pop(mid, None)
        if subscription is None:
            return
        if any(rc.is_failure for rc in reason_codes):
            self.subscription_status[subscription] = "refused"
            logging.error("MQTT broker refused subscription to %s (%s): check the account's ACL",
                          subscription, ", ".join(str(rc) for rc in reason_codes))
        else:
            self.subscription_status[subscription] = "ok"

    def add_handler(self, subscription, fn):
        """Subscribe to `subscription` and call fn(topic, payload_bytes) for each message on it.

        Handlers run on the MQTT network thread, so they must be quick and thread-safe.
        """
        self._handlers[subscription] = fn
        if self.client.is_connected():
            self._subscribe(subscription)

    def _on_message(self, client, userdata, msg):
        for subscription, fn in self._handlers.items():
            if mqtt.topic_matches_sub(subscription, msg.topic):
                try:
                    fn(msg.topic, msg.payload)
                except Exception:
                    logging.exception("MQTT handler for %s failed", subscription)
                return

        if mqtt.topic_matches_sub(self.config.SENSOR_TOPIC, msg.topic):
            if self.sensor_store.ingest(msg.topic, msg.payload) is None:
                logging.warning("Unparseable sensor message on %s: %r", msg.topic, msg.payload)
            return

        payload = msg.payload.decode(errors="replace")
        logging.info("MQTT message received on %s: %s", msg.topic, payload)
        self.last_message["topic"] = msg.topic
        self.last_message["payload"] = payload
        self.last_message["layout"] = None
        self.last_message["widgets"] = None

        try:
            parsed = json.loads(payload)
            if isinstance(parsed, dict):
                self.last_message["layout"] = parsed.get("layout")
                widgets = parsed.get("widgets")
                if isinstance(widgets, list):
                    self.last_message["widgets"] = widgets
        except (json.JSONDecodeError, TypeError):
            pass

        self.last_message["version"] += 1
        self.message_event.set()

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def run_forever(self):
        """Blocking loop; intended to be run on a background thread."""
        self.client.connect(self.config.MQTT_HOST, self.config.MQTT_PORT, keepalive=60)
        self.client.loop_forever()

    def start_background_thread(self):
        thread = threading.Thread(target=self.run_forever, daemon=True)
        thread.start()
        return thread
