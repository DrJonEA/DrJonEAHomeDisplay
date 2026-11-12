"""Test whether we can pull ISP speed and WAN throughput data from a UniFi gateway (UCG Ultra).

Uses the UniFi Network application API on UniFi OS (https://<host>/proxy/network/api/...).
Prints, for a quick look at what's available:

  1. ISP speed: the last speed test from the site health, plus the speed test history.
  2. Throughput: the current WAN rate, then totals, averages and peaks from the 5-minute and
     daily traffic reports.
  3. Latency monitors: the gateway's own internet latency checks (Google, Microsoft, ...), if
     they can be found in stat/health or stat/device.

Authentication (set one of these in the environment):
  UNIFI_API_KEY             API key (UniFi OS: Settings > Control Plane > Integrations).
  UNIFI_USER, UNIFI_PASSWD  A local UniFi OS account. Use a local-only, read-only ("View Only")
                            admin: Ubiquiti cloud accounts with MFA can't log in this way.
Optional:
  UNIFI_HOST                Gateway address (default 192.168.1.1)
  UNIFI_SITE                Site name (default "default")

The gateway uses a self-signed certificate, so TLS verification is off unless UNIFI_CA_FILE
points to a CA bundle that trusts it.

Usage:
  python3 unifiStats.py              # summary
  python3 unifiStats.py --days 14    # speed test history window (default 7)
  python3 unifiStats.py --raw        # also dump the raw JSON from each call
"""
import argparse
import json
import os
import statistics
import sys
import time
from datetime import datetime

import requests
import urllib3

HOST = os.environ.get("UNIFI_HOST", "192.168.1.1")
SITE = os.environ.get("UNIFI_SITE", "default")
API_KEY = os.environ.get("UNIFI_API_KEY")
USER = os.environ.get("UNIFI_USER")
PASSWD = os.environ.get("UNIFI_PASSWD")
CA_FILE = os.environ.get("UNIFI_CA_FILE")

BASE = "https://%s" % HOST
NETWORK = "%s/proxy/network/api/s/%s" % (BASE, SITE)


class UniFi:
    def __init__(self, raw=False):
        self.raw = raw
        self.session = requests.Session()
        self.session.verify = CA_FILE or False
        if not CA_FILE:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.auth = None

    def login(self):
        """Authenticate with the API key if set, else username/password. Returns a description."""
        if API_KEY:
            self.session.headers["X-API-KEY"] = API_KEY
            self.auth = "API key"
            return self.auth
        if not (USER and PASSWD):
            sys.exit("Set UNIFI_API_KEY, or UNIFI_USER and UNIFI_PASSWD")
        resp = self.session.post(
            "%s/api/auth/login" % BASE,
            json={"username": USER, "password": PASSWD, "rememberMe": False},
            timeout=10,
        )
        if resp.status_code != 200:
            sys.exit("Login failed: HTTP %d %s" % (resp.status_code, resp.text[:200]))
        # UniFi OS wants the CSRF token on POSTs made with the session cookie.
        csrf = resp.headers.get("X-Updated-CSRF-Token") or resp.headers.get("X-CSRF-Token")
        if csrf:
            self.session.headers["X-CSRF-Token"] = csrf
        self.auth = "user %s" % USER
        return self.auth

    def call(self, method, path, body=None):
        url = "%s/%s" % (NETWORK, path)
        resp = self.session.request(method, url, json=body, timeout=15)
        if resp.status_code == 401 and self.auth == "API key":
            raise RuntimeError(
                "HTTP 401 on %s: this firmware may not accept API keys on the Network API; "
                "try UNIFI_USER/UNIFI_PASSWD instead" % path)
        if resp.status_code != 200:
            raise RuntimeError("HTTP %d on %s: %s" % (resp.status_code, path, resp.text[:200]))
        data = resp.json()
        if self.raw:
            print("\n--- %s %s ---\n%s" % (method, path, json.dumps(data, indent=2)[:4000]))
        meta = data.get("meta", {})
        if meta.get("rc") not in (None, "ok"):
            raise RuntimeError("%s returned rc=%s %s" % (path, meta.get("rc"), meta.get("msg", "")))
        return data.get("data", [])

    def report(self, interval, kind, attrs, start, end):
        """stat/report/<interval>.<kind> between epoch seconds start..end."""
        return self.call("POST", "stat/report/%s.%s" % (interval, kind),
                         {"attrs": attrs + ["time"], "start": int(start * 1000), "end": int(end * 1000)})


def fmt_time(ms_or_s):
    if not ms_or_s:
        return "-"
    secs = ms_or_s / 1000 if ms_or_s > 1e11 else ms_or_s
    return datetime.fromtimestamp(secs).strftime("%a %d %b %H:%M")


def mbps_from_bytes(byte_count, seconds):
    return byte_count * 8 / seconds / 1e6


def fmt_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1000:
            return "%.1f %s" % (n, unit)
        n /= 1000
    return "%.1f PB" % n


def heading(text):
    print("\n" + text)
    print("=" * len(text))


def isp_speed(api, days):
    heading("1. ISP speed")
    health = {h.get("subsystem"): h for h in api.call("GET", "stat/health")}

    www = health.get("www", {})
    wan = health.get("wan", {})
    if www:
        print("Last speed test:  %s" % fmt_time(www.get("speedtest_lastrun")))
        print("  Download        %s Mbps" % www.get("xput_down", "-"))
        print("  Upload          %s Mbps" % www.get("xput_up", "-"))
        print("  Ping            %s ms" % www.get("speedtest_ping", "-"))
        print("  Status          %s" % www.get("speedtest_status", "-"))
        print("Internet latency: %s ms   uptime: %s s   drops: %s"
              % (www.get("latency", "-"), www.get("uptime", "-"), www.get("drops", "-")))
    else:
        print("No 'www' subsystem in stat/health (no speed test summary)")
    if wan:
        print("WAN:              %s  ISP: %s  status: %s"
              % (wan.get("wan_ip", "-"), wan.get("isp_name") or wan.get("isp_organization") or "-",
                 wan.get("status", "-")))

    end = time.time()
    tests = api.call("POST", "stat/report/archive.speedtest", {
        "attrs": ["xput_download", "xput_upload", "latency", "time"],
        "start": int((end - days * 86400) * 1000),
        "end": int(end * 1000),
    })
    tests = sorted(tests, key=lambda t: t.get("time", 0))
    print("\nSpeed test history, last %d days: %d test(s)" % (days, len(tests)))
    if not tests:
        print("  (none: is the scheduled speed test enabled? Settings > Internet > WAN > Speed Test)")
        return
    print("  %-17s %10s %10s %8s" % ("When", "Down Mbps", "Up Mbps", "Ping ms"))
    for t in tests[-10:]:
        print("  %-17s %10.1f %10.1f %8.0f" % (
            fmt_time(t.get("time")), t.get("xput_download", 0), t.get("xput_upload", 0), t.get("latency", 0)))
    if len(tests) > 10:
        print("  ... %d earlier" % (len(tests) - 10))
    for label, key in (("Download", "xput_download"), ("Upload", "xput_upload"), ("Ping", "latency")):
        values = [t[key] for t in tests if t.get(key) is not None]
        if values:
            print("  %-8s min %.1f  median %.1f  max %.1f" % (
                label, min(values), statistics.median(values), max(values)))


def throughput(api):
    heading("2. WAN throughput")
    health = {h.get("subsystem"): h for h in api.call("GET", "stat/health")}
    wan = health.get("wan", {})
    tx, rx = wan.get("tx_bytes-r"), wan.get("rx_bytes-r")
    if tx is not None and rx is not None:
        print("Now:  down %.2f Mbps   up %.2f Mbps" % (rx * 8 / 1e6, tx * 8 / 1e6))
    else:
        print("Now:  no current WAN rate in stat/health")

    end = time.time()
    # Site reports carry WAN bytes per interval: rx = download, tx = upload.
    for interval, seconds, span, label in (("5minutes", 300, 86400, "Last 24 hours (5-minute buckets)"),
                                           ("daily", 86400, 7 * 86400, "Last 7 days (daily buckets)")):
        rows = api.report(interval, "site", ["wan-rx_bytes", "wan-tx_bytes"], end - span, end)
        rows = [r for r in rows if "wan-rx_bytes" in r or "wan-tx_bytes" in r]
        print("\n%s: %d bucket(s)" % (label, len(rows)))
        if not rows:
            print("  (no WAN data in stat/report/%s.site)" % interval)
            continue
        for name, key in (("Download", "wan-rx_bytes"), ("Upload", "wan-tx_bytes")):
            vals = [r.get(key, 0) for r in rows]
            rates = [mbps_from_bytes(v, seconds) for v in vals]
            peak = max(range(len(rows)), key=lambda i: vals[i])
            print("  %-8s total %10s   avg %7.2f Mbps   peak %7.2f Mbps at %s" % (
                name, fmt_bytes(sum(vals)), statistics.mean(rates), rates[peak],
                fmt_time(rows[peak].get("time"))))
        if interval == "daily":
            print("  %-17s %12s %12s" % ("Day", "Down", "Up"))
            for r in sorted(rows, key=lambda r: r.get("time", 0)):
                print("  %-17s %12s %12s" % (fmt_time(r.get("time"))[:10],
                                             fmt_bytes(r.get("wan-rx_bytes", 0)),
                                             fmt_bytes(r.get("wan-tx_bytes", 0))))


def find_monitors(obj, path="", found=None):
    """Search UniFi JSON for monitor entries: dicts with a "target" and a latency value."""
    found = [] if found is None else found
    if isinstance(obj, dict):
        if isinstance(obj.get("target"), str):
            keys = [k for k in ("latency_average", "latency", "avg_latency") if isinstance(obj.get(k), (int, float))]
            if keys:
                found.append((path, obj))
        for k, v in obj.items():
            find_monitors(v, "%s.%s" % (path, k) if path else k, found)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_monitors(v, "%s[%d]" % (path, i), found)
    return found


def monitors(api):
    heading("3. Latency monitors")
    for source in ("stat/health", "stat/device"):
        found = find_monitors(api.call("GET", source))
        if found:
            print("Found %d in %s:" % (len(found), source))
            for path, m in found:
                latency = next(m[k] for k in ("latency_average", "latency", "avg_latency")
                               if isinstance(m.get(k), (int, float)))
                print("  %-22s %6.1f ms  availability %s   (%s)" % (
                    m["target"], latency, m.get("availability", "-"), path))
            return
        print("None in %s" % source)
    print("The manager will ping its own targets instead (WAN_PING_TARGETS).")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--days", type=int, default=7, help="speed test history window (days)")
    parser.add_argument("--raw", action="store_true", help="dump raw JSON from each API call")
    args = parser.parse_args()

    api = UniFi(raw=args.raw)
    print("UniFi %s  site %s  auth: %s" % (HOST, SITE, api.login()))

    ok = True
    for section, fn in (("ISP speed", lambda: isp_speed(api, args.days)), ("Throughput", lambda: throughput(api)),
                        ("Latency monitors", lambda: monitors(api))):
        try:
            fn()
        except (RuntimeError, requests.RequestException, ValueError) as exc:
            ok = False
            print("\n%s FAILED: %s" % (section, exc))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
