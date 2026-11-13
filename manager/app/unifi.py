"""External network view from a UniFi gateway (e.g. UCG Ultra), plus cloud latency.

Polled by the scheduler (see create_app). fetch_wan() collects:
  - ISP: name, WAN IP, internet latency, uptime and drops (stat/health "www"/"wan").
  - Speed tests: history from stat/report/archive.speedtest. The "last speed test" fields in
    stat/health read 0 / Idle on the UCG Ultra, so the latest history entry is used instead.
  - Throughput: current WAN rate, plus 5-minute (24h) and daily (7 days) WAN byte reports.
  - Cloud latency: the gateway's own internet monitors (Google, Microsoft, ...) when they can be
    found in the API, otherwise pinged locally with icmplib.

Uses the UniFi Network API on UniFi OS (https://<host>/proxy/network/api/...); see
exp/Unifi/unifiStats.py for a standalone version.
"""
import logging
import statistics
import time

import requests
import urllib3

SPEEDTEST_DAYS = 7
LOCAL_PING_COUNT = 5
LOCAL_PING_INTERVAL = 0.2
LOCAL_PING_TIMEOUT = 1.0
JSON_RETRIES = 3  # the gateway occasionally sends a damaged JSON body; ask again

# Short labels for well-known monitor targets: one letter fits the 3x5 tile font.
_TARGET_LABELS = [
    (("google",), "G"),
    (("microsoft", "office", "azure", "bing"), "M"),
    (("cloudflare", "1.1.1.1", "1.0.0.1"), "C"),
    (("amazon", "aws"), "A"),
    (("ui.com", "ubnt", "ubiquiti"), "U"),
    (("quad9", "9.9.9.9"), "Q"),
    (("facebook", "meta"), "F"),
]


def target_label(target):
    t = target.lower()
    for needles, label in _TARGET_LABELS:
        if any(n in t for n in needles):
            return label
    # Plain IPs (e.g. 8.8.8.8) get their first digit, which the tile font has.
    return t[0] if t[:1].isdigit() else "?"


class UniFiClient:
    def __init__(self, config):
        self.host = config.UNIFI_HOST
        self.site = config.UNIFI_SITE
        self.api_key = config.UNIFI_API_KEY
        self.user = config.UNIFI_USER
        self.passwd = config.UNIFI_PASSWD
        self.base = "https://%s" % self.host
        self.session = requests.Session()
        self.session.verify = config.UNIFI_CA_FILE or False
        if not config.UNIFI_CA_FILE:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if self.api_key:
            self.session.headers["X-API-KEY"] = self.api_key
        self._logged_in = bool(self.api_key)

    @staticmethod
    def configured(config):
        return bool(config.UNIFI_HOST and (config.UNIFI_API_KEY or (config.UNIFI_USER and config.UNIFI_PASSWD)))

    def _login(self):
        resp = self.session.post("%s/api/auth/login" % self.base, timeout=10,
                                 json={"username": self.user, "password": self.passwd, "rememberMe": False})
        if resp.status_code != 200:
            raise RuntimeError("UniFi login failed: HTTP %d" % resp.status_code)
        csrf = resp.headers.get("X-Updated-CSRF-Token") or resp.headers.get("X-CSRF-Token")
        if csrf:
            self.session.headers["X-CSRF-Token"] = csrf
        self._logged_in = True

    def call(self, method, path, body=None):
        if not self._logged_in:
            self._login()
        url = "%s/proxy/network/api/s/%s/%s" % (self.base, self.site, path)
        for attempt in range(1, JSON_RETRIES + 1):
            resp = self.session.request(method, url, json=body, timeout=15)
            if resp.status_code == 401 and not self.api_key:
                self._login()  # session expired
                resp = self.session.request(method, url, json=body, timeout=15)
            if resp.status_code != 200:
                raise RuntimeError("UniFi HTTP %d on %s" % (resp.status_code, path))
            try:
                data = resp.json()
                break
            except ValueError as exc:
                detail = "%s (%d bytes, Content-Length %s)" % (
                    exc, len(resp.content), resp.headers.get("Content-Length", "-"))
                if attempt == JSON_RETRIES:
                    raise RuntimeError("UniFi bad JSON from %s after %d attempts: %s" % (path, attempt, detail))
                logging.warning("UniFi bad JSON from %s (attempt %d/%d): %s; retrying",
                                path, attempt, JSON_RETRIES, detail)
                time.sleep(0.5 * attempt)
        rc = data.get("meta", {}).get("rc")
        if rc not in (None, "ok"):
            raise RuntimeError("UniFi %s returned rc=%s" % (path, rc))
        return data.get("data", [])

    def report(self, name, attrs, start, end):
        return self.call("POST", "stat/report/%s" % name,
                         {"attrs": attrs + ["time"], "start": int(start * 1000), "end": int(end * 1000)})


def _find_monitors(obj):
    """Search UniFi JSON for internet monitor entries: dicts with a "target" and a latency.

    On the UCG Ultra these sit in stat/health under wan.uptime_stats.WAN, in two lists:
    "monitors" (Microsoft, Google, Cloudflare: the console's internet latency view) and
    "alerting_monitors" (the WAN health checks, e.g. ping.ui.com, 1.1.1.1, 8.8.8.8). The console's
    monitors come first; alerting checks are added only for targets not already listed.
    """
    entries = []  # (is_alerting, order, entry)

    def walk(node, parent_key=""):
        if isinstance(node, dict):
            if isinstance(node.get("target"), str):
                latency = next((node[k] for k in ("latency_average", "latency", "avg_latency")
                                if isinstance(node.get(k), (int, float))), None)
                if latency is not None:
                    alerting = "alert" in parent_key
                    entries.append((alerting, len(entries), {
                        "target": node["target"],
                        "latency_ms": float(latency),
                        "availability": node.get("availability"),
                        "kind": "alerting" if alerting else "monitor",
                    }))
            for key, value in node.items():
                walk(value, key)
        elif isinstance(node, list):
            for value in node:
                walk(value, parent_key)

    walk(obj)
    found = {}
    for _, _, entry in sorted(entries, key=lambda e: (e[0], e[1])):
        found.setdefault(entry["target"], entry)
    return list(found.values())


def _local_pings(targets):
    from icmplib import multiping  # optional dependency, also used by the network sweep
    hosts = multiping(targets, count=LOCAL_PING_COUNT, interval=LOCAL_PING_INTERVAL,
                      timeout=LOCAL_PING_TIMEOUT, privileged=False)
    results = []
    for target, host in zip(targets, hosts):
        results.append({
            "target": target,
            "latency_ms": statistics.median(host.rtts) if host.rtts else None,
            "availability": 100.0 * (1 - host.packet_loss),
            "kind": "local ping",
        })
    return results


def fetch_wan(client, ping_targets, now=None):
    """Collect the external network view. Raises if the gateway can't be read at all."""
    now = time.time() if now is None else now
    health_list = client.call("GET", "stat/health")
    health = {h.get("subsystem"): h for h in health_list}
    www, wan = health.get("www", {}), health.get("wan", {})

    result = {
        "fetched": now,
        "isp": wan.get("isp_name") or wan.get("isp_organization"),
        "wan_ip": wan.get("wan_ip"),
        "status": wan.get("status"),
        "internet_status": www.get("status"),
        "latency_ms": www.get("latency"),
        "uptime_s": www.get("uptime"),
        "drops": www.get("drops"),
        "now_down_mbps": wan["rx_bytes-r"] * 8 / 1e6 if "rx_bytes-r" in wan else None,
        "now_up_mbps": wan["tx_bytes-r"] * 8 / 1e6 if "tx_bytes-r" in wan else None,
        "speedtests": [],
        "throughput_5min": [],
        "throughput_daily": [],
        "monitors": [],
        "monitor_source": None,
        "notes": [],
    }

    def attempt(label, fn):
        try:
            fn()
        except Exception as exc:  # keep whatever else we got
            logging.warning("UniFi %s failed: %s", label, exc)
            result["notes"].append("%s failed: %s" % (label, exc))

    def speedtests():
        rows = client.report("archive.speedtest", ["xput_download", "xput_upload", "latency"],
                             now - SPEEDTEST_DAYS * 86400, now)
        result["speedtests"] = sorted(
            ({"time": r["time"] / 1000, "down_mbps": r.get("xput_download"),
              "up_mbps": r.get("xput_upload"), "ping_ms": r.get("latency")} for r in rows if "time" in r),
            key=lambda r: r["time"])

    def throughput():
        for key, report, seconds, span in (("throughput_5min", "5minutes.site", 300, 86400),
                                           ("throughput_daily", "daily.site", 86400, 7 * 86400)):
            rows = client.report(report, ["wan-rx_bytes", "wan-tx_bytes"], now - span, now)
            result[key] = sorted(
                ({"time": r["time"] / 1000,
                  "down_bytes": r.get("wan-rx_bytes", 0), "up_bytes": r.get("wan-tx_bytes", 0),
                  "down_mbps": r.get("wan-rx_bytes", 0) * 8 / seconds / 1e6,
                  "up_mbps": r.get("wan-tx_bytes", 0) * 8 / seconds / 1e6}
                 for r in rows if "time" in r and ("wan-rx_bytes" in r or "wan-tx_bytes" in r)),
                key=lambda r: r["time"])

    def monitors():
        found = _find_monitors(health_list)
        if not found:
            found = _find_monitors(client.call("GET", "stat/device"))
        if found:
            result["monitors"], result["monitor_source"] = found, "UniFi gateway"

    attempt("speed test history", speedtests)
    attempt("throughput reports", throughput)
    attempt("gateway latency monitors", monitors)
    if not result["monitors"] and ping_targets:
        def local():
            result["monitors"], result["monitor_source"] = _local_pings(ping_targets), "local ping"
        attempt("local cloud pings", local)

    for m in result["monitors"]:
        m["label"] = target_label(m["target"])
    result["last_speedtest"] = result["speedtests"][-1] if result["speedtests"] else None
    return result
