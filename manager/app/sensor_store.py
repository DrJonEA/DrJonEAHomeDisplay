"""In-memory cache of sensor nodes and their recent readings.

Nodes publish on drjonea/sensor/<group>/<nodeId> with a JSON object such as
{"id": "studycosmic", "temperature": 21.5, "humidity": 46.8, "mbps": 8.1, "rssi": -58}.
Every field is optional. The store keeps each node's latest value per metric plus a
time-limited history for charting. It is fed from the MQTT thread and read from
Flask request threads, so all access goes through a lock.
"""
import json
import math
import threading
import time
from collections import deque

# Reported by the nodes themselves...
METRICS = ("temperature", "humidity", "mbps", "rssi")
# ...and measured by the manager's network sweep (see network_sweep.py).
PROBE_METRICS = ("mqtt_ms", "mqtt_loss", "icmp_ms", "icmp_loss")
ALL_METRICS = METRICS + PROBE_METRICS
HISTORY_SECONDS = 24 * 60 * 60
HISTORY_MAX_POINTS = 5000  # per node per metric; a backstop for chatty nodes
STALE_SECONDS = 10 * 60


def _parse_payload(raw):
    """Decode the first JSON object in the payload, ignoring any trailing junk."""
    text = raw.decode(errors="replace").strip()
    try:
        obj, _ = json.JSONDecoder().raw_decode(text)
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


def _number(value):
    """Return a finite float, or None for missing/non-numeric/NaN values."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if math.isfinite(value) else None


class SensorStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._nodes = {}
        self._next_slot = 0
        self.version = 0
        self._changed = threading.Condition(self._lock)

    def ingest(self, topic, raw_payload, now=None):
        """Record a sensor message. Returns the node id, or None if it was unusable."""
        now = time.time() if now is None else now
        data = _parse_payload(raw_payload)
        if data is None:
            return None

        parts = topic.split("/")
        node_id = str(data.get("id") or parts[-1])
        group = parts[2] if len(parts) > 3 else None

        readings = {m: _number(data.get(m)) for m in METRICS}
        readings = {m: v for m, v in readings.items() if v is not None}

        with self._lock:
            node = self._nodes.get(node_id)
            if node is None:
                node = {
                    "id": node_id,
                    # Fixed colour slot in order of first appearance, so a node keeps
                    # its colour as others come and go.
                    "slot": self._next_slot,
                    "latest": {},
                    "ip": None,
                    "history": {m: deque(maxlen=HISTORY_MAX_POINTS) for m in ALL_METRICS},
                }
                self._next_slot += 1
                self._nodes[node_id] = node
            node["group"] = group
            node["topic"] = topic
            node["last_seen"] = now
            for metric, value in readings.items():
                node["latest"][metric] = value
                node["history"][metric].append((now, value))
            self._prune(node, now)
            self.version += 1
            self._changed.notify_all()
        return node_id

    @staticmethod
    def _prune(node, now):
        cutoff = now - HISTORY_SECONDS
        for points in node["history"].values():
            while points and points[0][0] < cutoff:
                points.popleft()

    def snapshot(self, since=0.0, now=None):
        """Nodes with latest values, plus history points newer than `since`."""
        now = time.time() if now is None else now
        with self._lock:
            nodes = []
            for node in sorted(self._nodes.values(), key=lambda n: n["id"]):
                self._prune(node, now)
                nodes.append({
                    "id": node["id"],
                    "group": node["group"],
                    "topic": node["topic"],
                    "slot": node["slot"],
                    "ip": node["ip"],
                    "last_seen": node["last_seen"],
                    "stale": now - node["last_seen"] > STALE_SECONDS,
                    "latest": dict(node["latest"]),
                    "history": {
                        m: [[t, v] for t, v in pts if t > since]
                        for m, pts in node["history"].items()
                    },
                })
            return {"now": now, "version": self.version, "nodes": nodes}

    def record_probe(self, node_id, readings, ip=None, now=None):
        """Store manager-measured values (PROBE_METRICS) for a node already known from its sensor
        reports. A value of None clears that metric's latest value (e.g. no ICMP replies).
        Returns False if the node is unknown."""
        now = time.time() if now is None else now
        with self._lock:
            node = self._nodes.get(node_id)
            if node is None:
                return False
            if ip:
                node["ip"] = ip
            for metric, value in readings.items():
                if metric not in PROBE_METRICS:
                    continue
                value = _number(value)
                if value is None:
                    node["latest"].pop(metric, None)
                else:
                    node["latest"][metric] = value
                    node["history"][metric].append((now, value))
            self.version += 1
        return True

    def wait_for_report(self, node_id, after, timeout):
        """Block until `node_id` sends a message timestamped after `after`, or `timeout` expires.

        Returns the node's latest readings if it reported in time, else None.
        """
        def reported():
            node = self._nodes.get(node_id)
            return node is not None and node["last_seen"] > after

        with self._lock:
            if self._changed.wait_for(reported, timeout=timeout):
                return dict(self._nodes[node_id]["latest"])
            return None
