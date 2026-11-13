"""Family presence: who is home, from the devices connected to the UniFi gateway.

People and their devices are listed in a JSON file (PRESENCE_FILE, default manager/presence.json,
kept out of git because it holds device MACs; see presence.example.json):

    {"grace_minutes": 3,
     "people": [{"name": "Jon", "letter": "J", "macs": ["aa:bb:cc:dd:ee:ff"],
                 "client_names": ["Jons-Phone"]}]}

A person is home while any of their devices is in the gateway's connected-client list
(stat/sta), matched by MAC or by its name in the UniFi console (which catches a phone that
switches to a randomised MAC). Phones drop off Wi-Fi briefly when idle, so someone only counts
as away once none of their devices has been seen for `grace_minutes`.

PresenceTracker.update() is run every minute by the scheduler; each call returns a fresh
snapshot for the tile, dashboard and /presence. When someone changes from away to home, the
tracker calls on_arrival(names) after storing the new snapshot in `latest`, so a display told to
show the tile straight away gets the updated picture.
"""
import json
import logging
import time

DEFAULT_GRACE_MINUTES = 3


def norm_mac(mac):
    return str(mac).strip().lower().replace("-", ":")


def load_people(path):
    """Read the people file. Returns (people, grace_seconds); raises if it's missing or invalid."""
    with open(path) as f:
        cfg = json.load(f)
    people = []
    for i, p in enumerate(cfg.get("people", [])):
        name = str(p["name"])
        people.append({
            "name": name,
            "letter": str(p.get("letter") or name[:1]).upper()[:1],
            "macs": [norm_mac(m) for m in p.get("macs", []) if m],
            "client_names": [str(n).lower() for n in p.get("client_names", []) if n],
            "slot": i,
        })
    if not people:
        raise ValueError("no people listed in %s" % path)
    return people, float(cfg.get("grace_minutes", DEFAULT_GRACE_MINUTES)) * 60


def arrival_text(names):
    """Scroll text for people who've just come home: "Jon is home", "Jon and Kevin are home"."""
    if len(names) == 1:
        return "%s is home" % names[0]
    return "%s and %s are home" % (", ".join(names[:-1]), names[-1])


def _client_matches(client, person):
    if norm_mac(client.get("mac", "")) in person["macs"]:
        return True
    names = {str(client.get(k, "")).lower() for k in ("name", "hostname", "display_name")}
    return bool(names & set(person["client_names"]))


class PresenceTracker:
    def __init__(self, client, people, grace_seconds, on_arrival=None):
        self.client = client
        self.people = people
        self.grace = grace_seconds
        self.on_arrival = on_arrival
        self.latest = None
        self.last_arrival = None   # {"names": [...], "time": epoch}
        self._state = {p["name"]: {"home": None, "since": None, "last_seen": None} for p in people}
        self._bootstrapped = False

    def _bootstrap(self, now):
        """On the first poll, take each person's last-seen time from the gateway's client records,
        so someone who left 5 minutes before start-up isn't shown as away straight away."""
        for p in self.people:
            latest = None
            for mac in p["macs"]:
                try:
                    rows = self.client.call("GET", "stat/user/%s" % mac)
                except RuntimeError:
                    continue
                seen = rows[0].get("last_seen") if rows else None
                if seen and (latest is None or seen > latest):
                    latest = seen
            self._state[p["name"]]["last_seen"] = latest
        self._bootstrapped = True

    def update(self, now=None):
        now = time.time() if now is None else now
        if not self._bootstrapped:
            self._bootstrap(now)
        connected = self.client.call("GET", "stat/sta")

        people = []
        arrivals = []
        for p in self.people:
            state = self._state[p["name"]]
            devices = [c for c in connected if _client_matches(c, p)]
            if devices:
                state["last_seen"] = now
            home = state["last_seen"] is not None and now - state["last_seen"] <= self.grace
            if home != state["home"]:
                if state["home"] is None:
                    # First reading: date it from the connection start, or from when they left.
                    if devices and "uptime" in devices[0]:
                        state["since"] = now - max(d.get("uptime", 0) for d in devices)
                    else:
                        state["since"] = state["last_seen"]
                else:
                    # Away: date it from when they were last seen, not when the grace ran out.
                    state["since"] = now if home else (state["last_seen"] or now)
                    logging.info("Presence: %s is now %s", p["name"], "home" if home else "away")
                    if home:
                        arrivals.append(p["name"])
                state["home"] = home
            people.append({
                "name": p["name"],
                "letter": p["letter"],
                "slot": p["slot"],
                "configured": bool(p["macs"] or p["client_names"]),
                "home": home,
                "since": state["since"],
                "last_seen": state["last_seen"],
                "devices": [{
                    "name": d.get("name") or d.get("hostname") or d.get("mac"),
                    "mac": d.get("mac"),
                    "ip": d.get("ip"),
                    "network": d.get("essid") or ("wired" if d.get("is_wired") else None),
                    "signal": d.get("signal"),
                } for d in devices],
            })
        if arrivals:
            self.last_arrival = {"names": arrivals, "time": now}
        self.latest = {"updated": now, "grace_minutes": self.grace / 60, "people": people,
                       "last_arrival": self.last_arrival}
        if arrivals and self.on_arrival:
            try:
                self.on_arrival(arrivals)
            except Exception:
                logging.exception("Presence arrival announcement failed")
        return self.latest
