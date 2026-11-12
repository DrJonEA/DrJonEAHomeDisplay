"""Periodic network sweep across the sensor nodes: MQTT ping, ICMP ping, then speed tests.

1. MQTT ping: publish {"id": n} to the displays' group ping topic and time each node's pong on
   TNG/<nodeId>/TPC/PONG (which may also carry its "ip"). Several rounds; the median per node is
   stored as `mqtt_ms`, and the share of pings with no pong as `mqtt_loss` (%). This is the full application round trip (manager -> broker -> node ->
   broker -> manager), including firmware scheduling and WiFi power saving.
2. ICMP ping: echo each node at the IP from its pong; the median is stored as `icmp_ms` and the
   loss as `icmp_loss` (%). This is the network round trip alone, for comparison.
3. Speed test: send {"speedtest": true} to each node's own display topic (e.g.
   drjonea/display/cosmic/studycosmic). It POSTs 100 KB to /speedtest and reports the rate as
   `mbps` in its next sensor message (~10s later). Nodes are tested one at a time, waiting for
   each report, so uploads never compete and skew each other.

Pings run first, while the network is quiet, so the speed test uploads can't inflate them.
The sweep runs on its own thread because a pass takes ~12s per node plus ~15s of pinging,
which would otherwise hold up the shared scheduler thread (e.g. the per-minute TZ publish).
"""
import json
import logging
import random
import statistics
import threading
import time

PING_TOPIC = "GRP/display/TPC/PING"
PONG_TOPIC = "TNG/+/TPC/PONG"
MQTT_PING_ROUNDS = 5
MQTT_PING_INTERVAL_SECONDS = 1.0
MQTT_PING_WAIT_SECONDS = 3.0        # after the last round, for stragglers
ICMP_COUNT = 10
ICMP_INTERVAL_SECONDS = 0.2
ICMP_TIMEOUT_SECONDS = 1.0

SPEEDTEST_PAYLOAD = json.dumps({"speedtest": True})
REPORT_TIMEOUT_SECONDS = 30
# Ignore a report arriving this soon after the command: it was already in flight, so it
# carries the previous mbps rather than this test's result.
MIN_REPORT_DELAY_SECONDS = 2
GAP_SECONDS = 2


def display_topic_for(sensor_topic):
    """drjonea/sensor/<group>/<node> -> drjonea/display/<group>/<node>; None if not a sensor topic."""
    parts = sensor_topic.split("/")
    if len(parts) < 3 or parts[1] != "sensor":
        return None
    parts[1] = "display"
    return "/".join(parts)


class _PongCollector:
    """Matches pongs to the ping ids we sent; fed from the MQTT network thread."""

    def __init__(self):
        self._lock = threading.Lock()
        self._sent = {}       # ping id -> monotonic send time
        self.rtts = {}        # node id -> [ms, ...]
        self.ips = {}         # node id -> ip

    def sent(self, ping_id):
        with self._lock:
            self._sent[ping_id] = time.monotonic()

    def on_pong(self, topic, payload):
        received = time.monotonic()
        parts = topic.split("/")      # TNG/<nodeId>/TPC/PONG
        if len(parts) < 2:
            return
        try:
            data = json.loads(payload)
        except ValueError:
            return
        if not isinstance(data, dict):
            return
        node_id = parts[1]
        with self._lock:
            sent = self._sent.get(data.get("id"))
            if sent is None:
                return  # someone else's ping, or one from an earlier sweep
            self.rtts.setdefault(node_id, []).append((received - sent) * 1000.0)
            if data.get("ip"):
                self.ips[node_id] = str(data["ip"])

    def results(self):
        with self._lock:
            return {n: list(r) for n, r in self.rtts.items()}, dict(self.ips)


STAGES = ("mqtt", "icmp", "speed")
STAGE_LABELS = {"mqtt": "MQTT ping", "icmp": "ICMP ping", "speed": "Speed test"}
HISTORY_RUNS = 10


def _stats(samples):
    if not samples:
        return {"median": None, "min": None, "max": None}
    return {"median": statistics.median(samples), "min": min(samples), "max": max(samples)}


class SweepRun:
    """What one sweep did and found, for the dashboard. Written by the sweep thread only;
    readers take a deep copy via as_dict() under the lock."""

    def __init__(self, run_id, trigger, stages, nodes):
        self._lock = threading.Lock()
        self.data = {
            "id": run_id,
            "trigger": trigger,                 # "schedule" or "manual"
            "stages": list(stages),
            "started": time.time(),
            "finished": None,
            "status": "running",                # running | done | no nodes | failed
            "current": None,                    # e.g. "Speed test: kitchen"
            "notes": [],                        # stage-level problems (e.g. ICMP unavailable)
            "nodes": {n["id"]: {"ip": n.get("ip"), "mqtt": None, "icmp": None, "speed": None}
                      for n in nodes},
        }

    def update(self, fn):
        with self._lock:
            fn(self.data)

    def node(self, node_id, stage, result):
        def apply(d):
            d["nodes"].setdefault(node_id, {"ip": None, "mqtt": None, "icmp": None, "speed": None})
            d["nodes"][node_id][stage] = result
            if result.get("ip"):
                d["nodes"][node_id]["ip"] = result["ip"]
        self.update(apply)

    def as_dict(self):
        with self._lock:
            return json.loads(json.dumps(self.data))


class NetworkSweep:
    def __init__(self, mqtt_service, sensor_store,
                 report_timeout=REPORT_TIMEOUT_SECONDS, gap=GAP_SECONDS):
        self.mqtt_service = mqtt_service
        self.sensor_store = sensor_store
        self.report_timeout = report_timeout
        self.gap = gap
        self._thread = None
        self._lock = threading.Lock()
        self._collector = None
        self._ping_id = random.randrange(1, 1_000_000)  # avoid clashing with ad-hoc test pingers
        self._run_seq = 0
        self._runs = []          # most recent last, at most HISTORY_RUNS
        self.schedule_minutes = None  # set by whoever schedules the sweep, for "next run" display
        mqtt_service.add_handler(PONG_TOPIC, self._on_pong)

    def _on_pong(self, topic, payload):
        collector = self._collector
        if collector is not None:
            collector.on_pong(topic, payload)

    @property
    def running(self):
        return self._thread is not None and self._thread.is_alive()

    def runs(self):
        """Recent runs, newest first, as plain dicts."""
        with self._lock:
            runs = list(self._runs)
        return [r.as_dict() for r in reversed(runs)]

    def start(self, stages=STAGES, trigger="schedule"):
        """Kick off a sweep in the background. Returns False if one is already running."""
        stages = tuple(s for s in STAGES if s in stages)
        with self._lock:
            if self.running:
                logging.warning("Network sweep still running; not starting a %s run", trigger)
                return False
            self._thread = threading.Thread(
                target=self.run, args=(stages, trigger), name="network-sweep", daemon=True)
            self._thread.start()
            return True

    def run(self, stages=STAGES, trigger="schedule"):
        """One sweep (blocking)."""
        nodes = [n for n in self.sensor_store.snapshot(since=time.time())["nodes"] if not n["stale"]]
        with self._lock:
            self._run_seq += 1
            run = SweepRun(self._run_seq, trigger, stages, nodes)
            self._runs = (self._runs + [run])[-HISTORY_RUNS:]
        try:
            if not nodes:
                logging.info("Network sweep: no live sensor nodes")
                run.update(lambda d: d.update(status="no nodes"))
                return
            logging.info("Network sweep (%s: %s) starting for %d node(s)",
                         trigger, ", ".join(stages), len(nodes))
            known = {n["id"] for n in nodes}
            ips = None
            if "mqtt" in stages:
                ips = self.mqtt_ping(known, run)
            if "icmp" in stages:
                if ips is None:
                    ips = self._known_ips(known, {})
                self.icmp_ping(ips, run)
            if "speed" in stages:
                self.speed_tests(nodes, run)
            run.update(lambda d: d.update(status="done"))
            logging.info("Network sweep finished")
        except Exception as exc:
            logging.exception("Network sweep failed")
            run.update(lambda d: d.update(status="failed") or d["notes"].append("Sweep failed: %s" % exc))
        finally:
            run.update(lambda d: d.update(finished=time.time(), current=None))

    def _known_ips(self, known, ips):
        """Add IPs learned in earlier sweeps for nodes not in `ips`."""
        for node in self.sensor_store.snapshot(since=time.time())["nodes"]:
            if node["id"] in known and node["ip"] and node["id"] not in ips:
                ips[node["id"]] = node["ip"]
        return {n: ip for n, ip in ips.items() if n in known}

    # --- 1. MQTT ping -------------------------------------------------------------------

    def mqtt_ping(self, known, run):
        """Group-ping the displays; store median RTT per node. Returns {node id: ip}."""
        if self.mqtt_service.subscription_status.get(PONG_TOPIC) == "refused":
            # Pinging would only record every node as 100% lost, blaming the nodes for a broker
            # ACL problem. Skip, and clear old MQTT figures so tiles show "not measured".
            note = ("MQTT ping skipped: the broker refused this account's subscription to %s, "
                    "so no pongs can be received. Allow it in the broker's ACL." % PONG_TOPIC)
            logging.error(note)
            run.update(lambda d: d["notes"].append(note))
            for node_id in known:
                self.sensor_store.record_probe(node_id, {"mqtt_ms": None, "mqtt_loss": None})
            return self._known_ips(known, {})
        run.update(lambda d: d.update(current="MQTT ping (%d rounds)" % MQTT_PING_ROUNDS))
        collector = _PongCollector()
        self._collector = collector
        try:
            for i in range(MQTT_PING_ROUNDS):
                if i:
                    time.sleep(MQTT_PING_INTERVAL_SECONDS)
                self._ping_id += 1
                collector.sent(self._ping_id)
                self.mqtt_service.publish(PING_TOPIC, json.dumps({"id": self._ping_id}))
            time.sleep(MQTT_PING_WAIT_SECONDS)
        finally:
            self._collector = None
        rtts, ips = collector.results()

        strangers = sorted(set(rtts) - known)
        if strangers:
            logging.info("MQTT ping: pongs from %s, which have no sensor reports; not stored", strangers)
            run.update(lambda d: d["notes"].append(
                "MQTT ping: pongs from nodes with no sensor reports (not stored): " + ", ".join(strangers)))
        for node_id in sorted(known):
            samples = rtts.get(node_id, [])
            stats = _stats(samples)
            loss = 100.0 * max(MQTT_PING_ROUNDS - len(samples), 0) / MQTT_PING_ROUNDS
            self.sensor_store.record_probe(
                node_id, {"mqtt_ms": stats["median"], "mqtt_loss": loss}, ip=ips.get(node_id))
            run.node(node_id, "mqtt", dict(stats, sent=MQTT_PING_ROUNDS, received=len(samples),
                                           loss=loss, ip=ips.get(node_id)))
            if not samples:
                logging.warning("MQTT ping: no pong from %s", node_id)
            else:
                logging.info("MQTT ping: %s %.1f ms median (%d/%d pongs)",
                             node_id, stats["median"], len(samples), MQTT_PING_ROUNDS)
        return self._known_ips(known, ips)

    # --- 2. ICMP ping -------------------------------------------------------------------

    def icmp_ping(self, ips, run):
        if not ips:
            logging.info("ICMP ping: no node IPs known (pongs carry them); skipping")
            run.update(lambda d: d["notes"].append(
                "ICMP ping skipped: no node IPs known (they come from the MQTT pongs)"))
            return
        run.update(lambda d: d.update(current="ICMP ping (%d echoes)" % ICMP_COUNT))
        try:
            from icmplib import multiping
            hosts = multiping(list(set(ips.values())), count=ICMP_COUNT, interval=ICMP_INTERVAL_SECONDS,
                              timeout=ICMP_TIMEOUT_SECONDS, privileged=False)
        except Exception as exc:  # missing library, or the OS refuses unprivileged ICMP sockets
            logging.warning("ICMP ping failed: %s", exc)
            run.update(lambda d: d["notes"].append("ICMP ping failed: %s" % exc))
            return
        by_ip = {h.address: h for h in hosts}
        for node_id, ip in sorted(ips.items()):
            host = by_ip.get(ip)
            if host is None:
                continue
            stats = _stats(host.rtts)
            loss = host.packet_loss * 100
            self.sensor_store.record_probe(node_id, {"icmp_ms": stats["median"], "icmp_loss": loss}, ip=ip)
            run.node(node_id, "icmp", dict(stats, sent=host.packets_sent, received=host.packets_received,
                                           loss=loss, jitter=host.jitter if host.rtts else None, ip=ip))
            if stats["median"] is None:
                logging.warning("ICMP ping: no replies from %s (%s)", node_id, ip)
            else:
                logging.info("ICMP ping: %s (%s) %.1f ms median, %.0f%% loss", node_id, ip, stats["median"], loss)

    # --- 3. Speed tests -----------------------------------------------------------------

    @staticmethod
    def _speed(status, topic=None, mbps=None, elapsed=None):
        return {"status": status, "topic": topic, "mbps": mbps, "elapsed": elapsed}

    def speed_tests(self, nodes, run):
        for node in nodes:
            run.node(node["id"], "speed", self._speed("pending"))
        for i, node in enumerate(nodes):
            topic = display_topic_for(node["topic"])
            if topic is None:
                logging.warning("Speed test: can't derive display topic for %s (%s)", node["id"], node["topic"])
                run.node(node["id"], "speed", self._speed("skipped: no display topic"))
                continue
            if i:
                time.sleep(self.gap)
            run.update(lambda d, n=node["id"]: d.update(current="Speed test: %s" % n))
            run.node(node["id"], "speed", self._speed("testing", topic))
            sent_at = time.time()
            self.mqtt_service.publish(topic, SPEEDTEST_PAYLOAD)
            latest = self.sensor_store.wait_for_report(
                node["id"], sent_at + MIN_REPORT_DELAY_SECONDS, self.report_timeout)
            mbps = latest.get("mbps") if latest else None
            elapsed = time.time() - sent_at
            if latest is None:
                status = "no report within %ds" % self.report_timeout
                logging.warning("Speed test: no report from %s within %ds", node["id"], self.report_timeout)
            elif mbps is None:
                status = "reported without mbps"
                logging.warning("Speed test: %s reported without mbps (%.1fs)", node["id"], elapsed)
            else:
                status = "ok"
                logging.info("Speed test: %s %.2f Mbps (%.1fs)", node["id"], mbps, elapsed)
            run.node(node["id"], "speed", self._speed(status, topic, mbps, elapsed))
