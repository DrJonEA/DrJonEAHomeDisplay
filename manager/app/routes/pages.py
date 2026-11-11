"""Dashboard page routes."""
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, render_template

from .. import calendar_themes
from ..display_presets import PRESETS, preset_payload_json


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

    @bp.route("/")
    def index():
        return render_template(
            "index.html",
            message=mqtt_service.last_message,
            topic=mqtt_service.config.MQTT_TOPIC,
            presets=PRESETS,
            preset_payload_json=preset_payload_json,
            calendar=_calendar_today(),
        )

    return bp
