"""Network sweep routes: status (JSON and dashboard fragment) and manual re-runs."""
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for

from ..network_sweep import STAGE_LABELS, STAGES

RUN_CHOICES = {"all": STAGES, "speed": ("speed",), "ping": ("mqtt", "icmp")}


def next_run(now, minutes):
    """Epoch of the next scheduled slot (minutes past the hour, UTC, as the scheduler uses)."""
    start = int(now // 60) * 60 + 60
    for offset in range(0, 120 * 60, 60):
        t = start + offset
        if time.gmtime(t).tm_min in minutes:
            return t
    return None


def network_sweep_context():
    """Template variables for the network sweep panel."""
    sweep = current_app.network_sweep
    tz = ZoneInfo(current_app.mqtt_service.config.DISPLAY_TIMEZONE)

    def fmt_time(epoch):
        return datetime.fromtimestamp(epoch, tz).strftime("%a %H:%M:%S") if epoch else "-"

    runs = sweep.runs()
    for run in runs:
        run["stage_text"] = ", ".join(STAGE_LABELS[s] for s in run["stages"])
        run["speed_summary"] = ", ".join(
            "%s %.1f" % (node_id, r["speed"]["mbps"])
            for node_id, r in sorted(run["nodes"].items())
            if r["speed"] and r["speed"].get("mbps") is not None
        ) or "-"
    return {
        "sweep_running": sweep.running,
        "sweep_runs": runs,
        "sweep_last": runs[0] if runs else None,
        "sweep_next": next_run(time.time(), sweep.schedule_minutes) if sweep.schedule_minutes else None,
        "fmt_time": fmt_time,
    }


def create_network_blueprint():
    bp = Blueprint("network", __name__)

    @bp.route("/network-sweep")
    def status():
        ctx = network_sweep_context()
        return jsonify({"running": ctx["sweep_running"], "next_run": ctx["sweep_next"], "runs": ctx["sweep_runs"]})

    @bp.route("/network-sweep/panel")
    def panel():
        return render_template("_network_sweep.html", **network_sweep_context())

    @bp.route("/network-sweep/run", methods=["POST"])
    def run():
        stages = RUN_CHOICES.get(request.form.get("stages", "all"), STAGES)
        started = current_app.network_sweep.start(stages=stages, trigger="manual")
        return redirect(url_for("pages.index", sweep="started" if started else "busy", _anchor="network"))

    return bp
