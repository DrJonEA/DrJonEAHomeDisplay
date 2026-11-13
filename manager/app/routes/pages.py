"""Dashboard page routes."""
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template, request

from .. import calendar_themes
from ..display_presets import PRESETS, preset_payload_json
from .network import network_sweep_context
from .presence import presence_context
from .wan import wan_context


def create_pages_blueprint(mqtt_service):
    bp = Blueprint("pages", __name__)

    def _calendar_today():
        """Today's date in the display's timezone, the calendar theme it gets, and what that hides."""
        config = mqtt_service.config
        day = datetime.now(ZoneInfo(config.DISPLAY_TIMEZONE)).date()
        try:
            theme, others = calendar_themes.describe_day(
                calendar_themes.load_collections(config.CALENDAR_THEMES_DIR),
                day,
                config.CALENDAR_IMAGE_DIR,
                config.DISPLAY_TIMEZONE,
            )
        except Exception as exc:  # never let a theme problem take the dashboard down
            return {"date": day, "error": str(exc)}
        return {
            "date": day,
            "title": theme.title or theme.name,
            "collection": theme.collection,
            "collection_description": theme.collection_description,
            # "tolkien: annual 23/11" -> "annual 23/11"
            "rule": theme.rule.split(": ", 1)[-1] if theme.collection else "no rule matched",
            "image": theme.image_path and theme.image_path.rsplit("/", 1)[-1],
            "others": others,
        }

    def _sensor_nodes():
        """Cached sensor nodes for the dashboard, with a human-readable age."""
        snapshot = mqtt_service.sensor_store.snapshot(since=time.time())  # no history needed
        for node in snapshot["nodes"]:
            age = int(snapshot["now"] - node["last_seen"])
            node["age"] = "%ds" % age if age < 120 else "%dm" % (age // 60) if age < 7200 else "%dh" % (age // 3600)
        return snapshot["nodes"]

    def _defcon():
        from flask import current_app
        state = current_app.defcon.snapshot()
        tz = ZoneInfo(mqtt_service.config.DISPLAY_TIMEZONE)
        for key in ("evaluated", "sent", "changed"):
            state[key + "_text"] = datetime.fromtimestamp(state[key], tz).strftime("%H:%M:%S") if state.get(key) else "-"
        state["interval"] = mqtt_service.config.DEFCON_INTERVAL_SECONDS
        return state

    @bp.route("/")
    def index():
        return render_template(
            "index.html",
            message=mqtt_service.last_message,
            topic=mqtt_service.config.MQTT_TOPIC,
            presets=PRESETS,
            preset_payload_json=preset_payload_json,
            calendar=_calendar_today(),
            sensor_nodes=_sensor_nodes(),
            sensor_topic=mqtt_service.config.SENSOR_TOPIC,
            sweep_flash=request.args.get("sweep"),
            **network_sweep_context(),
            **wan_context(),
            **presence_context(),
            defcon=_defcon(),
        )

    return bp
