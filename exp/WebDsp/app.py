import logging
import threading
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, stream_with_context, send_from_directory
import paho.mqtt.client as mqtt
import json
import time
import sys
import os


# Grab environment variables
clientId=os.environ.get("MQTT_CLIENT")
user=os.environ.get("MQTT_USER")
passwd=os.environ.get("MQTT_PASSWD")
host= os.environ.get("MQTT_HOST")
port=int(os.environ.get("MQTT_PORT"))
print("MQTT %s:%d"%(host,port))
if (len(clientId) > 6):
   print("Client: %s..."%clientId[0:4])
else: 
   print("Client: %s..."%clientId)   
if (len(user) > 6):
   print("User: %s..."%user[0:4])
else:
    print("User: %s"%user) 

MQTT_BROKER = host
MQTT_PORT = port
MQTT_TOPIC = "home/display"


app = Flask(__name__)

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id = clientId)
mqtt_client.username_pw_set(username=user, password=passwd)
last_message = {"topic": None, "payload": None, "layout": None, "widgets": None, "version": 0}
message_event = threading.Event()


def on_connect(client, userdata, flags, rc, properties):
    logging.info("MQTT connected: %s", mqtt.connack_string(rc))
    if rc == 0:
        client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="replace")
    logging.info("MQTT message received on %s: %s", msg.topic, payload)
    last_message["topic"] = msg.topic
    last_message["payload"] = payload
    last_message["layout"] = None
    last_message["widgets"] = None

    try:
        parsed = json.loads(payload)
        if isinstance(parsed, dict):
            last_message["layout"] = parsed.get("layout")
            widgets = parsed.get("widgets")
            if isinstance(widgets, list):
                last_message["widgets"] = widgets
    except (json.JSONDecodeError, TypeError):
        pass

    last_message["version"] += 1
    message_event.set()


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def mqtt_thread():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    mqtt_client.loop_forever()


@app.route("/")
def index():
    return render_template("index.html", message=last_message, topic=MQTT_TOPIC)


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)


@app.route("/publish", methods=["POST"])
def publish():
    topic = request.form.get("topic", MQTT_TOPIC)
    payload = request.form.get("payload", "")
    if payload:
        mqtt_client.publish(topic, payload)
    return redirect(url_for("index"))


@app.route("/latest")
def latest():
    return jsonify({
        "topic": last_message["topic"],
        "payload": last_message["payload"],
        "layout": last_message["layout"],
        "widgets": last_message["widgets"],
        "version": last_message["version"],
    })


@app.route("/events")
def events():
    last_id_header = request.headers.get("Last-Event-ID")
    try:
        last_id = int(last_id_header) if last_id_header else 0
    except ValueError:
        last_id = 0

    @stream_with_context
    def event_stream(last_id):
        while True:
            if last_message["version"] > last_id:
                payload_data = {
                    "topic": last_message["topic"],
                    "payload": last_message["payload"],
                    "layout": last_message["layout"],
                    "widgets": last_message["widgets"],
                    "version": last_message["version"],
                }
                data = json.dumps(payload_data)
                yield f"id: {last_message['version']}\n"
                yield f"data: {data}\n\n"
                last_id = last_message["version"]
            else:
                message_event.wait(timeout=15)
                message_event.clear()
                if last_message["version"] <= last_id:
                    yield ": keep-alive\n\n"

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(event_stream(last_id), headers=headers)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    thread = threading.Thread(target=mqtt_thread, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=5080, debug=True, use_reloader=False)
