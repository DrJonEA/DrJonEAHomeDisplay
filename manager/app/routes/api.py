"""JSON/SSE API routes for the live dashboard (publish, latest, events)."""
import json

from flask import Blueprint, Response, jsonify, redirect, request, stream_with_context, url_for


def create_api_blueprint(mqtt_service):
    bp = Blueprint("api", __name__)

    @bp.route("/publish", methods=["POST"])
    def publish():
        topic = request.form.get("topic", mqtt_service.config.MQTT_TOPIC)
        payload = request.form.get("payload", "")
        if payload:
            mqtt_service.publish(topic, payload)
        return redirect(url_for("pages.index"))

    @bp.route("/latest")
    def latest():
        return jsonify(_snapshot())

    @bp.route("/events")
    def events():
        last_id_header = request.headers.get("Last-Event-ID")
        try:
            last_id = int(last_id_header) if last_id_header else 0
        except ValueError:
            last_id = 0

        @stream_with_context
        def event_stream(last_id):
            while True:
                if mqtt_service.last_message["version"] > last_id:
                    data = json.dumps(_snapshot())
                    yield f"id: {mqtt_service.last_message['version']}\n"
                    yield f"data: {data}\n\n"
                    last_id = mqtt_service.last_message["version"]
                else:
                    mqtt_service.message_event.wait(timeout=15)
                    mqtt_service.message_event.clear()
                    if mqtt_service.last_message["version"] <= last_id:
                        yield ": keep-alive\n\n"

        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
        return Response(event_stream(last_id), headers=headers)

    def _snapshot():
        m = mqtt_service.last_message
        return {
            "topic": m["topic"],
            "payload": m["payload"],
            "layout": m["layout"],
            "widgets": m["widgets"],
            "version": m["version"],
        }

    return bp
