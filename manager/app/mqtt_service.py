"""MQTT connectivity and last-message state for the display manager."""
import json
import logging
import threading

import paho.mqtt.client as mqtt


class MqttService:
    """Wraps the paho MQTT client, tracking the most recent display message."""

    def __init__(self, config):
        self.config = config
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

    def _on_connect(self, client, userdata, flags, rc, properties):
        logging.info("MQTT connected: %s", mqtt.connack_string(rc))
        if rc == 0:
            client.subscribe(self.config.MQTT_TOPIC)

    def _on_message(self, client, userdata, msg):
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
