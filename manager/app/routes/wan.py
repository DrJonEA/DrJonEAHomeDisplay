"""External network (UniFi gateway) routes: JSON, manual refresh, and dashboard panel context."""
import statistics
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, current_app, jsonify, redirect, url_for

from .network import next_run


def _summary(rows, key_bytes, key_mbps):
    if not rows:
        return None
    peak = max(rows, key=lambda r: r[key_mbps])
    return {
        "total_bytes": sum(r[key_bytes] for r in rows),
        "avg_mbps": statistics.mean(r[key_mbps] for r in rows),
        "peak_mbps": peak[key_mbps],
        "peak_time": peak["time"],
    }


def fmt_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1000:
            return "%.1f %s" % (n, unit)
        n /= 1000
    return "%.1f PB" % n


def fmt_duration(seconds):
    if seconds is None:
        return "-"
    days, rem = divmod(int(seconds), 86400)
    return "%dd %dh" % (days, rem // 3600) if days else "%dh %dm" % (rem // 3600, rem % 3600 // 60)


def wan_context():
    """Template variables for the External Network panel."""
    app = current_app
    tz = ZoneInfo(app.mqtt_service.config.DISPLAY_TIMEZONE)

    def fmt_time(epoch, pattern="%a %H:%M"):
        return datetime.fromtimestamp(epoch, tz).strftime(pattern) if epoch else "-"

    ctx = {"wan_enabled": app.wan_enabled, "wan": None, "wan_error": None, "wan_updated": None,
           "wan_fmt_time": fmt_time, "fmt_bytes": fmt_bytes, "fmt_duration": fmt_duration}
    if not app.wan_enabled:
        return ctx
    wan, updated, error = app.scheduler.get("wan")
    ctx.update(wan=wan, wan_error=error, wan_updated=updated)
    if wan:
        five = wan.get("throughput_5min", [])
        ctx["wan_24h"] = {"down": _summary(five, "down_bytes", "down_mbps"),
                          "up": _summary(five, "up_bytes", "up_mbps")}
        ctx["wan_days"] = list(reversed(wan.get("throughput_daily", [])))
        ctx["wan_tests"] = list(reversed(wan.get("speedtests", [])))[:10]
        ctx["wan_next"] = next_run(time.time(), app.wan_minutes)
    return ctx


def create_wan_blueprint():
    bp = Blueprint("wan", __name__)

    @bp.route("/wan")
    def status():
        if not current_app.wan_enabled:
            return jsonify({"enabled": False}), 404
        wan, updated, error = current_app.scheduler.get("wan")
        return jsonify({"enabled": True, "updated": updated, "error": error, "data": wan})

    @bp.route("/wan/refresh", methods=["POST"])
    def refresh():
        if current_app.wan_enabled:
            current_app.scheduler.refresh_now("wan")
        return redirect(url_for("pages.index", _anchor="wan"))

    return bp
