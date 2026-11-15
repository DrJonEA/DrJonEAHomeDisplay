"""Family presence routes: JSON, manual refresh, and dashboard panel context."""
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, current_app, jsonify, redirect, url_for

from ..presence import arrival_text


def _ago(epoch, now):
    if not epoch:
        return "-"
    secs = int(now - epoch)
    if secs < 120:
        return "%ds ago" % secs
    if secs < 7200:
        return "%dm ago" % (secs // 60)
    if secs < 172800:
        return "%dh %dm ago" % (secs // 3600, secs % 3600 // 60)
    return "%dd ago" % (secs // 86400)


def presence_context():
    """Template variables for the Family Presence panel."""
    app = current_app
    ctx = {"presence_enabled": app.presence_enabled, "presence_setup_error": app.presence_error,
           "presence": None, "presence_error": None}
    if not app.presence_enabled:
        return ctx
    tz = ZoneInfo(app.mqtt_service.config.DISPLAY_TIMEZONE)
    presence, updated, error = app.scheduler.get("presence")
    now = time.time()
    if presence:
        for p in presence["people"]:
            p["since_text"] = (datetime.fromtimestamp(p["since"], tz).strftime("%a %H:%M")
                               if p.get("since") else "start-up")
            p["seen_text"] = _ago(p.get("last_seen"), now)
        arrival = presence.get("last_arrival")
        if arrival:
            ctx["presence_arrival"] = "%s at %s" % (
                arrival_text(arrival["names"]), datetime.fromtimestamp(arrival["time"], tz).strftime("%a %H:%M"))
    ctx.update(presence=presence, presence_error=error,
               presence_updated=datetime.fromtimestamp(updated, tz).strftime("%H:%M:%S") if updated else "-")
    return ctx


def create_presence_blueprint():
    bp = Blueprint("presence", __name__)

    @bp.route("/presence")
    def status():
        if not current_app.presence_enabled:
            return jsonify({"enabled": False, "error": current_app.presence_error}), 404
        presence, updated, error = current_app.scheduler.get("presence")
        return jsonify({"enabled": True, "updated": updated, "error": error, "data": presence})

    @bp.route("/presence/refresh", methods=["POST"])
    def refresh():
        if current_app.presence_enabled:
            current_app.scheduler.refresh_now("presence")
        return redirect(url_for("pages.index", _anchor="presence"))

    return bp
