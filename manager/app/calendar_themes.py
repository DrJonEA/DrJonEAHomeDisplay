"""Calendar tile themes: chooses a background image and text styling for a given date.

Themes live in a directory of JSON "collection" files (Config.CALENDAR_THEMES_DIR, default
manager/calendar_themes/), e.g. weekdays.json, advent.json, birthdays.json. Every *.json file
there is loaded, and re-read on every request so edits apply without a restart.

A collection file:
  {
    "priority": 50,                    # breaks ties between collections (higher wins); default 0
    "enabled": true,                   # false switches the whole collection off
    "defaults": {"outline": "#000000"},  # merged into every theme in this file
    "themes":   {"xmas": {...}},       # optional named themes, reusable from any collection
    "dates":    {"25/12/2026": ...},   # a specific date            dd/mm/yyyy
    "events":   {"easter": ...},       # a computed moveable event  (see astro_events.py)
    "annual":   {"25/12": ...},        # the same day every year    dd/mm
    "weekdays": {"monday": ...},       # day of the week            name or 3+ letter prefix
    "default":  ...                    # used when no rule in any collection matches
  }
Each rule value is either an inline theme object or the name of a named theme.

Choosing a theme for a day:
  1. Rule kind decides first: dates > events > annual > weekdays. So a specific date always
     overrides an annual day, which overrides a day of the week, whichever files they are in.
  2. Between rules of the same kind, the collection with the higher priority wins (then the
     file name, alphabetically). E.g. birthdays (100) beat Tolkien anniversaries (50) on 13/01.
  3. If nothing matches, the highest-priority collection's "default" is used, else a plain tile.
A matching rule whose theme is unusable (unknown name, bad colour) is skipped with a warning,
so lookup falls through to the next candidate. tools/calendar_report.py shows, for a whole
year, which theme each day gets and what it hides.

A theme:
  {
    "title":   "Christmas Day",          # optional, for reports/logs
    "image":   "christmas.png",          # in Config.CALENDAR_IMAGE_DIR; omit for plain black
    "outline": "#000000",                # optional 1px text outline, for legibility on busy images
    "text": {                            # optional per-field overrides; null hides that field
      "dow":   {"color": "#c8c8ff", "pos": [1, -1]},
      "day":   {"color": "#ffffff", "pos": [19, -1]},
      "month": {"color": "#ffff32", "pos": [1, 9]}
    }
  }
Colours are "#rrggbb" or [r, g, b]. Images should be 32x22 (the bottom 10 rows of the tile are
reserved for the device's clock); other sizes are scaled and cropped to fit.
"""
import json
import logging
import os
from dataclasses import dataclass, field, replace
from datetime import datetime

from .astro_events import EVENT_NAMES, events_for_year

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
RULE_KINDS = ("dates", "events", "annual", "weekdays")  # in precedence order

# Positions keep glyphs (incl. descenders and a 1px outline) within rows 0-21.
DEFAULT_TEXT = {
    "dow": {"color": (200, 200, 255), "pos": (1, -1)},
    "day": {"color": (255, 255, 255), "pos": (19, -1)},
    "month": {"color": (255, 255, 50), "pos": (1, 9)},
}


@dataclass(frozen=True)
class CalendarTheme:
    name: str
    image_path: str = None
    outline: tuple = None
    # field -> {"color": (r, g, b), "pos": (x, y)}; a hidden field is absent
    text: dict = field(default_factory=lambda: dict(DEFAULT_TEXT))
    rule: str = "builtin"  # which rule matched, e.g. "advent: annual 25/12", for logging/preview
    title: str = None
    collection: str = None              # collection whose rule chose this theme
    collection_description: str = None


PLAIN_THEME = CalendarTheme(name="plain")


@dataclass
class Collection:
    name: str
    priority: int = 0
    description: str = None
    defaults: dict = field(default_factory=dict)
    themes: dict = field(default_factory=dict)
    rules: dict = field(default_factory=dict)  # kind -> {key: theme ref}
    default: object = None


@dataclass(frozen=True)
class Match:
    """A rule that matches a day; `ref` is an inline theme dict or a theme name."""
    kind: str
    key: str
    ref: object
    collection: Collection

    @property
    def rule(self):
        return "%s: %s %s" % (self.collection.name, self.kind.rstrip("s"), self.key)


def _warn_duplicates(path):
    def hook(pairs):
        seen = set()
        for key, _ in pairs:
            if key in seen:
                logging.warning("Calendar themes %s: duplicate key %r (the later one wins)", path, key)
            seen.add(key)
        return dict(pairs)
    return hook


def _load_collection(path):
    name = os.path.splitext(os.path.basename(path))[0]
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh, object_pairs_hook=_warn_duplicates(path))
    except (OSError, ValueError) as exc:
        logging.warning("Calendar themes file %s unreadable: %s", path, exc)
        return None
    if not isinstance(data, dict):
        logging.warning("Calendar themes file %s: top level must be an object", path)
        return None
    if not data.get("enabled", True):
        return None
    return Collection(
        name=name,
        priority=int(data.get("priority", 0)),
        description=data.get("description"),
        defaults=data.get("defaults") or {},
        themes=data.get("themes") or {},
        rules={kind: data.get(kind) or {} for kind in RULE_KINDS},
        default=data.get("default"),
    )


def load_collections(path):
    """Load every enabled collection from a directory of *.json files (or a single file),
    highest priority first. A missing path yields no collections (plain tiles)."""
    if os.path.isdir(path):
        files = sorted(os.path.join(path, f) for f in os.listdir(path) if f.endswith(".json"))
    elif os.path.isfile(path):
        files = [path]
    else:
        logging.info("Calendar themes not found: %s", path)
        files = []
    collections = [c for c in (_load_collection(f) for f in files) if c is not None]
    collections.sort(key=lambda c: (-c.priority, c.name))
    return collections


def _named_themes(collections):
    """Theme name -> (spec, defining collection); the highest-priority definition wins."""
    named = {}
    for coll in collections:
        for name, spec in coll.themes.items():
            if name in named:
                logging.warning("Calendar theme %r defined in both %s and %s; using %s",
                                name, named[name][1].name, coll.name, named[name][1].name)
                continue
            named[name] = (spec, coll)
    return named


def _parse_color(value):
    if value is None:
        return None
    if isinstance(value, str):
        hex_value = value.lstrip("#")
        if len(hex_value) != 6:
            raise ValueError("colour %r must be #rrggbb" % value)
        return tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return tuple(int(c) for c in value)
    raise ValueError("colour %r must be #rrggbb or [r, g, b]" % (value,))


def _match_weekday(key, weekday_index):
    key = key.strip().lower()
    return len(key) >= 3 and WEEKDAYS[weekday_index].startswith(key)


def _rule_matches(kind, key, day, todays_events):
    if kind == "dates":
        try:
            return datetime.strptime(key.strip(), "%d/%m/%Y").date() == day
        except ValueError:
            logging.warning("Calendar themes: bad date key %r (want dd/mm/yyyy)", key)
            return False
    if kind == "events":
        if key not in EVENT_NAMES:
            logging.warning("Calendar themes: unknown event %r (known: %s)", key, ", ".join(sorted(EVENT_NAMES)))
            return False
        return todays_events[key] == day
    if kind == "annual":
        try:
            d, m = (int(part) for part in key.strip().split("/"))
        except ValueError:
            logging.warning("Calendar themes: bad annual key %r (want dd/mm)", key)
            return False
        return (d, m) == (day.day, day.month)
    return _match_weekday(key, day.weekday())


def find_matches(collections, day, zone_name="UTC"):
    """Every rule matching `day`, best first (rule kind, then collection priority)."""
    todays_events = events_for_year(day.year, zone_name)
    matches = []
    for kind in RULE_KINDS:
        for coll in collections:  # already highest priority first
            for key, ref in coll.rules[kind].items():
                if _rule_matches(kind, key, day, todays_events):
                    matches.append(Match(kind, key, ref, coll))
    return matches


def _build_theme(name, spec, rule, image_dir):
    image_path = None
    if spec.get("image"):
        image_path = os.path.join(image_dir, spec["image"])
        if not os.path.isfile(image_path):
            logging.warning("Calendar theme '%s': image not found: %s", name, image_path)
            image_path = None

    text = {}
    overrides = spec.get("text") or {}
    for field_name, defaults in DEFAULT_TEXT.items():
        if field_name in overrides and overrides[field_name] is None:
            continue  # explicitly hidden
        override = overrides.get(field_name) or {}
        color = _parse_color(override["color"]) if "color" in override else defaults["color"]
        pos = tuple(int(v) for v in override["pos"]) if "pos" in override else defaults["pos"]
        text[field_name] = {"color": color, "pos": pos}

    return CalendarTheme(
        name=name,
        image_path=image_path,
        outline=_parse_color(spec.get("outline")),
        text=text,
        rule=rule,
        title=spec.get("title"),
    )


def build_theme(ref, collection, rule, collections, image_dir):
    """Turn a rule's theme reference (inline dict or theme name) into a CalendarTheme.

    Raises ValueError if the reference or theme is unusable.
    """
    if isinstance(ref, str):
        named = _named_themes(collections)
        if ref not in named:
            raise ValueError("unknown theme %r" % ref)
        spec, owner = named[ref]
        name = ref
    elif isinstance(ref, dict):
        spec, owner = ref, collection
        name = rule
    else:
        raise ValueError("theme must be a name or an object, not %r" % (ref,))
    if not isinstance(spec, dict):
        raise ValueError("theme %r must be an object" % name)
    return _build_theme(name, {**owner.defaults, **spec}, rule, image_dir)


def resolve_theme(collections, day, image_dir, zone_name="UTC"):
    """Return the CalendarTheme for date `day`, falling back to a plain tile if nothing usable matches.

    `zone_name` is the display's IANA timezone, used to put computed events on the right local day.
    """
    return describe_day(collections, day, image_dir, zone_name)[0]


def describe_day(collections, day, image_dir, zone_name="UTC"):
    """Return (theme, others) for `day`: the chosen CalendarTheme, and the (title, rule) of every
    other matching non-weekday rule it takes precedence over (e.g. for showing on a dashboard)."""
    matches = find_matches(collections, day, zone_name)
    candidates = [(m.ref, m.collection, m.rule) for m in matches]
    candidates += [(c.default, c, "%s: default" % c.name) for c in collections if c.default is not None]
    theme = PLAIN_THEME
    for ref, coll, rule in candidates:
        try:
            theme = build_theme(ref, coll, rule, collections, image_dir)
        except (ValueError, TypeError, KeyError) as exc:
            logging.warning("Calendar themes: %s skipped: %s", rule, exc)
            continue
        theme = replace(theme, collection=coll.name, collection_description=coll.description)
        break
    others = []
    for m in matches:
        if m.rule == theme.rule or m.kind == "weekdays":
            continue
        title = m.ref.get("title") if isinstance(m.ref, dict) else m.ref
        others.append((title or "untitled", m.rule))
    return theme, others
