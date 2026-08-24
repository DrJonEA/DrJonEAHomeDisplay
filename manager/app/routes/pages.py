"""Dashboard page routes."""
from flask import Blueprint, render_template

from ..display_presets import PRESETS, preset_payload_json


def create_pages_blueprint(mqtt_service):
    bp = Blueprint("pages", __name__)

    @bp.route("/")
    def index():
        return render_template(
            "index.html",
            message=mqtt_service.last_message,
            topic=mqtt_service.config.MQTT_TOPIC,
            presets=PRESETS,
            preset_payload_json=preset_payload_json,
        )

    return bp
