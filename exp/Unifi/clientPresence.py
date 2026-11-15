"""Test whether a device (e.g. a phone) is currently connected, using a UniFi gateway (UCG Ultra).

Looks the device up by MAC and/or by its name in the UniFi console:
  - stat/sta          clients connected right now (present = listed here)
  - stat/user/<mac>   the gateway's record of a known client, for "last seen" when it's away

A match on name as well as MAC catches a phone that has switched to a randomised ("private")
Wi-Fi MAC: the console name may follow it, the MAC won't.

Uses the same environment variables as unifiStats.py (UNIFI_API_KEY, or UNIFI_USER and
UNIFI_PASSWD; UNIFI_HOST, UNIFI_SITE).

Usage:
  python3 clientPresence.py --mac aa:bb:cc:dd:ee:ff
  python3 clientPresence.py --name "My-Phone"
  python3 clientPresence.py --mac aa:bb:cc:dd:ee:ff --watch 30    # poll, print changes
  python3 clientPresence.py --mac aa:bb:cc:dd:ee:ff --raw         # also dump the raw JSON

Exit code: 0 connected, 1 not connected, 2 error.
"""
import argparse
import sys
import time
from datetime import datetime

import requests

from unifiStats import HOST, SITE, UniFi


def norm_mac(mac):
    return mac.strip().lower().replace("-", ":")


def is_randomised(mac):
    """Locally administered bit set: a randomised/private MAC rather than the hardware one."""
    try:
        return bool(int(mac.split(":")[0], 16) & 0x02)
    except ValueError:
        return False


def ago(epoch):
    if not epoch:
        return "-"
    secs = int(time.time() - epoch)
    if secs < 120:
        return "%ds ago" % secs
    if secs < 7200:
        return "%dm ago" % (secs // 60)
    if secs < 172800:
        return "%dh %dm ago" % (secs // 3600, secs % 3600 // 60)
    return "%dd ago" % (secs // 86400)


def fmt_time(epoch):
    return datetime.fromtimestamp(epoch).strftime("%a %d %b %H:%M:%S") if epoch else "-"


def fmt_duration(secs):
    if secs is None:
        return "-"
    h, rem = divmod(int(secs), 3600)
    return "%dh %dm" % (h, rem // 60) if h else "%dm %ds" % (rem // 60, rem % 60)


def matches(client, mac, name):
    if mac and norm_mac(client.get("mac", "")) == mac:
        return True
    if name:
        wanted = name.lower()
        return any(wanted == str(client.get(k, "")).lower() for k in ("name", "hostname", "display_name"))
    return False


def find_connected(api, mac, name):
    """Connected clients matching the MAC or name."""
    return [c for c in api.call("GET", "stat/sta") if matches(c, mac, name)]


def known_record(api, mac):
    """The gateway's stored record for this MAC (exists even when the device is away)."""
    if not mac:
        return None
    try:
        rows = api.call("GET", "stat/user/%s" % mac)
    except RuntimeError:
        return None
    return rows[0] if rows else None


def describe(client):
    wired = client.get("is_wired")
    print("  Name       %s" % (client.get("name") or client.get("display_name") or "-"))
    print("  Hostname   %s" % client.get("hostname", "-"))
    print("  MAC        %s%s" % (client.get("mac"), "  (randomised)" if is_randomised(client.get("mac", "")) else ""))
    print("  IP         %s" % client.get("ip", "-"))
    print("  Network    %s" % (client.get("essid") or client.get("network") or "-"))
    if wired:
        print("  Link       wired, switch %s port %s" % (client.get("sw_mac", "-"), client.get("sw_port", "-")))
    else:
        print("  Link       Wi-Fi %s ch %s, AP %s" % (client.get("radio_proto", client.get("radio", "-")),
                                                    client.get("channel", "-"), client.get("ap_mac", "-")))
        print("  Signal     %s dBm   tx %s / rx %s Mbps" % (
            client.get("signal", "-"),
            round(client["tx_rate"] / 1000) if "tx_rate" in client else "-",
            round(client["rx_rate"] / 1000) if "rx_rate" in client else "-"))
    print("  Connected  %s (for %s)" % (fmt_time(time.time() - client["uptime"]) if "uptime" in client else "-",
                                       fmt_duration(client.get("uptime"))))
    print("  Last seen  %s" % ago(client.get("last_seen")))


def check(api, mac, name, verbose=True):
    """Returns (connected, clients)."""
    clients = find_connected(api, mac, name)
    if not verbose:
        return bool(clients), clients
    if clients:
        print("CONNECTED")
        for c in clients:
            describe(c)
            if mac and norm_mac(c.get("mac", "")) != mac:
                print("  Note: matched by name, but the MAC differs from %s" % mac)
    else:
        print("NOT CONNECTED")
        rec = known_record(api, mac)
        if rec:
            print("  Known as   %s" % (rec.get("name") or rec.get("hostname") or "-"))
            print("  Last seen  %s (%s)" % (fmt_time(rec.get("last_seen")), ago(rec.get("last_seen"))))
            print("  First seen %s" % fmt_time(rec.get("first_seen")))
        elif mac:
            print("  The gateway has no record of %s" % mac)
    return bool(clients), clients


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mac", help="device MAC address")
    parser.add_argument("--name", help="device name as shown in the UniFi console")
    parser.add_argument("--watch", type=int, metavar="SECONDS", help="poll every SECONDS and print changes")
    parser.add_argument("--raw", action="store_true", help="dump raw JSON from each API call")
    args = parser.parse_args()
    if not (args.mac or args.name):
        parser.error("give --mac and/or --name")
    mac = norm_mac(args.mac) if args.mac else None

    api = UniFi(raw=args.raw)
    print("UniFi %s  site %s  auth: %s" % (HOST, SITE, api.login()))
    print("Looking for %s" % " / ".join(x for x in (mac, args.name) if x))
    if mac and is_randomised(mac):
        print("Note: %s is a randomised (private) MAC; it can change per network or over time." % mac)
    print()

    try:
        connected, _ = check(api, mac, args.name)
        if not args.watch:
            sys.exit(0 if connected else 1)
        print("\nWatching every %ds (Ctrl-C to stop)..." % args.watch)
        while True:
            time.sleep(args.watch)
            now_connected, clients = check(api, mac, args.name, verbose=False)
            if now_connected != connected:
                state = "CONNECTED" if now_connected else "DISCONNECTED"
                detail = ""
                if clients:
                    c = clients[0]
                    detail = "  %s  %s  %s dBm" % (c.get("ip", "-"), c.get("essid", "wired"), c.get("signal", "-"))
                print("%s  %s%s" % (datetime.now().strftime("%H:%M:%S"), state, detail))
                connected = now_connected
    except KeyboardInterrupt:
        print()
    except (RuntimeError, requests.RequestException) as exc:
        print("ERROR: %s" % exc)
        sys.exit(2)


if __name__ == "__main__":
    main()
