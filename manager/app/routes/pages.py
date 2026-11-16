"""Dashboard page routes."""
import json
import re
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

from .. import calendar_themes
from ..display_presets import COSMIC_TOPIC, PRESETS, preset_payload_json

CALENDAR_AHEAD_DAYS = 6
# A tile's display path: "home", or path segments ending .brg565 (fetched as <server>/32x32/<path>).
TILE_DATA = re.compile(r"home|[A-Za-z0-9_-]+(/[A-Za-z0-9_.-]+)*\.brg565")
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
        for r in snapshot["rejected"]:
            age = int(snapshot["now"] - r["last"])
            r["age"] = "%ds" % age if age < 120 else "%dm" % (age // 60) if age < 7200 else "%dh" % (age // 3600)
        return snapshot["nodes"], snapshot["rejected"]

    def _calendar_ahead():
        """The next CALENDAR_AHEAD_DAYS days after today, with the theme each one gets."""
        config = mqtt_service.config
        today = datetime.now(ZoneInfo(config.DISPLAY_TIMEZONE)).date()
        try:
            collections = calendar_themes.load_collections(config.CALENDAR_THEMES_DIR)
        except Exception:
            collections = None
        days = []
        for offset in range(1, CALENDAR_AHEAD_DAYS + 1):
            day = today + timedelta(days=offset)
            title = None
            if collections is not None:
                try:
                    theme = calendar_themes.resolve_theme(collections, day, config.CALENDAR_IMAGE_DIR,
                                                          config.DISPLAY_TIMEZONE)
                    title = theme.title or theme.name
                except Exception:
                    pass
            days.append({"date": day, "iso": day.isoformat(), "title": title})
        return days

    def _defcon():
        state = current_app.defcon.snapshot()
        tz = ZoneInfo(mqtt_service.config.DISPLAY_TIMEZONE)
        for key in ("evaluated", "sent", "changed"):
            state[key + "_text"] = datetime.fromtimestamp(state[key], tz).strftime("%H:%M:%S") if state.get(key) else "-"
        state["interval"] = mqtt_service.config.DEFCON_INTERVAL_SECONDS
        if state.get("manual"):
            state["manual"]["at_text"] = datetime.fromtimestamp(state["manual"]["at"], tz).strftime("%H:%M:%S")
        return state

    @bp.route("/defcon/set", methods=["POST"])
    def defcon_set():
        """Send a DEFCON level chosen on the dashboard; the next automatic update replaces it."""
        try:
            current_app.defcon.set_manual(int(request.form.get("level", "")))
        except ValueError:
            pass
        return redirect(url_for("pages.index", _anchor="defcon"))

    @bp.route("/tiles/show", methods=["POST"])
    def tile_show():
        """Send the clicked dashboard tile to the Cosmic displays. `data` is the display path, e.g.
        "weather.brg565" or "env/hallsensor.brg565"; calendar tiles get the clock overlay, like the
        calendar preset."""
        data = request.form.get("data", "")
        if not TILE_DATA.fullmatch(data) or ".." in data:
            return jsonify({"error": "not a tile path: %r" % data}), 400
        widgets = [{"type": "img", "data": data}]
        if data == "cal.brg565" or data.startswith("cal/"):
            widgets.append({"type": "clock"})
        mqtt_service.publish(COSMIC_TOPIC, json.dumps({"layout": "layout2", "widgets": widgets}))
        return jsonify({"sent": data, "topic": COSMIC_TOPIC})

    @bp.route("/calendar/show", methods=["POST"])
    def calendar_show():
        """Show one day's calendar tile (with the clock, like the calendar preset) on the Cosmic displays."""
        try:
            day = datetime.strptime(request.form.get("date", ""), "%Y-%m-%d").date()
        except ValueError:
            return redirect(url_for("pages.index", _anchor="calendar-today"))
        payload = {"layout": "layout2", "widgets": [
            {"type": "img", "data": "cal/%s.brg565" % day.isoformat()},
            {"type": "clock"},
        ]}
        mqtt_service.publish(COSMIC_TOPIC, json.dumps(payload))
        return redirect(url_for("pages.index", shown=day.isoformat(), _anchor="calendar-today"))

    @bp.route("/")
    def index():
        nodes, sensor_rejected = _sensor_nodes()
        return render_template(
            "index.html",
            message=mqtt_service.last_message,
            topic=mqtt_service.config.MQTT_TOPIC,
            presets=PRESETS,
            preset_payload_json=preset_payload_json,
            calendar=_calendar_today(),
            calendar_ahead=_calendar_ahead(),
            calendar_shown=request.args.get("shown"),
            sensor_nodes=nodes,
            sensor_rejected=sensor_rejected,
            sensor_groups=sorted({n["group"] for n in nodes if n.get("group")}),
            sensor_topic=mqtt_service.config.SENSOR_TOPIC,
            sweep_flash=request.args.get("sweep"),
            **network_sweep_context(),
            **wan_context(),
            **presence_context(),
            defcon=_defcon(),
        )

    return bp
