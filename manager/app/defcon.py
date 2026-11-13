"""Central DEFCON status for the displays: 5 is all well, lower is worse.

The level starts at 5 and is raised (the number lowered) by current issues:
  - each person away (family presence)                                  +1 each
  - slow WAN: internet or cloud latency at/above DEFCON_SLOW_LATENCY_MS, a
    cloud target not replying, or the last ISP speed test below
    DEFCON_SLOW_DOWN_MBPS / DEFCON_SLOW_UP_MBPS                         +1 (once)
  - WAN problem: gateway reports WAN or internet not "ok", or no cloud
    target replies at all                                               straight to level 2
It never goes below DEFCON_MIN_LEVEL (2 for now; level 1 is reserved).

People with no devices configured aren't counted, and missing data (presence or WAN not read
yet, or the gateway unreachable) is reported as a reason but doesn't change the level: the
manager can't tell a problem from a gap in what it can see.

DefconMonitor re-evaluates every DEFCON_INTERVAL_SECONDS and publishes {"defcon": n} to the
displays. It pauses while a network sweep runs: every display command restarts the firmware's
10s sensor-report timer, which the speed tests wait on.
"""
import json
import logging
import threading
import time

MAX_LEVEL = 5
WAN_STALE_SECONDS = 15 * 60


def compute_defcon(presence, wan, wan_updated, cfg, now=None):
    """Return {"level", "reasons": [{"text", "effect"}]}. Pure: no I/O, for testing."""
    now = time.time() if now is None else now
    reasons = []
    raise_by = 0
    wan_problem = False

    # Family presence
    if presence is None:
        reasons.append({"text": "Presence not available", "effect": "none"})
    else:
        for p in presence.get("people", []):
            if not p.get("configured", True) or p.get("home") is None:
                continue
            if not p["home"]:
                raise_by += 1
                reasons.append({"text": "%s is away" % p["name"], "effect": "+1"})

    # WAN
    if wan is None or wan_updated is None or now - wan_updated > WAN_STALE_SECONDS:
        reasons.append({"text": "WAN data unavailable", "effect": "none"})
    else:
        for key, label in (("status", "WAN"), ("internet_status", "Internet")):
            status = wan.get(key)
            if status not in (None, "ok"):
                wan_problem = True
                reasons.append({"text": "%s status: %s" % (label, status), "effect": "level 2"})
        monitors = wan.get("monitors") or []
        if monitors and all(m.get("latency_ms") is None for m in monitors):
            wan_problem = True
            reasons.append({"text": "No cloud targets reachable", "effect": "level 2"})

        slow = []
        latency = wan.get("latency_ms")
        if latency is not None and latency >= cfg.DEFCON_SLOW_LATENCY_MS:
            slow.append("internet latency %d ms" % latency)
        if not wan_problem:
            for m in monitors:
                if m.get("latency_ms") is None:
                    slow.append("%s not replying" % m["target"])
                elif m["latency_ms"] >= cfg.DEFCON_SLOW_LATENCY_MS:
                    slow.append("%s %d ms" % (m["target"], m["latency_ms"]))
        test = wan.get("last_speedtest") or {}
        if test.get("down_mbps") is not None and test["down_mbps"] < cfg.DEFCON_SLOW_DOWN_MBPS:
            slow.append("ISP download %.0f Mbps" % test["down_mbps"])
        if test.get("up_mbps") is not None and test["up_mbps"] < cfg.DEFCON_SLOW_UP_MBPS:
            slow.append("ISP upload %.0f Mbps" % test["up_mbps"])
        if slow:
            raise_by += 1
            reasons.append({"text": "Slow WAN: " + ", ".join(slow), "effect": "+1"})

    level = MAX_LEVEL - raise_by
    if wan_problem:
        level = min(level, 2)
    level = max(level, cfg.DEFCON_MIN_LEVEL)
    return {"level": level, "reasons": reasons}


class DefconMonitor:
    def __init__(self, cfg, mqtt_service, topic, get_presence, get_wan, is_paused):
        self.cfg = cfg
        self.mqtt_service = mqtt_service
        self.topic = topic
        self.get_presence = get_presence      # () -> presence snapshot or None
        self.get_wan = get_wan                # () -> (wan dict or None, updated epoch or None)
        self.is_paused = is_paused            # () -> True while sending would disturb tests
        self.state = {"level": None, "reasons": [], "evaluated": None, "sent": None,
                      "paused": False, "changed": None}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

    def evaluate(self, now=None):
        now = time.time() if now is None else now
        wan, wan_updated = self.get_wan()
        result = compute_defcon(self.get_presence(), wan, wan_updated, self.cfg, now)
        with self._lock:
            if result["level"] != self.state["level"]:
                if self.state["level"] is not None:
                    logging.info("DEFCON %s -> %s: %s", self.state["level"], result["level"],
                                 "; ".join(r["text"] for r in result["reasons"]) or "all clear")
                self.state["changed"] = now
            self.state.update(result, evaluated=now)
        return result

    def tick(self, now=None):
        """Evaluate and, unless paused, publish. Returns the level sent, or None if paused."""
        now = time.time() if now is None else now
        result = self.evaluate(now)
        paused = self.is_paused()
        with self._lock:
            self.state["paused"] = paused
        if paused:
            return None
        self.mqtt_service.publish(self.topic, json.dumps({"defcon": result["level"]}))
        with self._lock:
            self.state["sent"] = now
        return result["level"]

    def snapshot(self):
        with self._lock:
            return json.loads(json.dumps(self.state))

    def _run(self):
        while not self._stop.is_set():
            try:
                self.tick()
            except Exception:
                logging.exception("DEFCON update failed")
            self._stop.wait(self.cfg.DEFCON_INTERVAL_SECONDS)

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, name="defcon", daemon=True)
            self._thread.start()

    def stop(self):
        self._stop.set()
