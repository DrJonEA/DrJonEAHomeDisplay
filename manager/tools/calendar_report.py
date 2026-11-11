"""Report which calendar theme each day of a year gets, what it hides, and config problems.

Usage:  python tools/calendar_report.py [YEAR] [--all]

By default lists only days with a special theme (anything beyond the weekday themes) or with a
clash; --all lists every day. Then checks for missing images, images nothing uses, unknown
theme names and unusable themes. Exits non-zero if any problem is found, so it can be used
as a pre-deploy check. Reads the same settings as the app (CALENDAR_THEMES_DIR, etc.).
"""
import logging
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import calendar_themes as ct  # noqa: E402
from app.config import Config  # noqa: E402


class _Collect(logging.Handler):
    """Gather the loader's warnings so they are reported (once each) rather than interleaved."""

    def __init__(self):
        super().__init__(logging.WARNING)
        self.messages = []

    def emit(self, record):
        msg = record.getMessage()
        if msg not in self.messages:
            self.messages.append(msg)


def _describe(match, collections):
    ref = match.ref
    title = ref.get("title") if isinstance(ref, dict) else ref
    try:
        ct.build_theme(ref, match.collection, match.rule, collections, Config.CALENDAR_IMAGE_DIR)
        note = ""
    except (ValueError, TypeError, KeyError) as exc:
        note = "  [UNUSABLE: %s]" % exc
    return "%s (%s)%s" % (title or "untitled", match.rule, note)


def main(argv):
    show_all = "--all" in argv
    years = [a for a in argv if a.isdigit()]
    year = int(years[0]) if years else date.today().year

    warnings = _Collect()
    logging.getLogger().addHandler(warnings)
    logging.getLogger().setLevel(logging.WARNING)

    collections = ct.load_collections(Config.CALENDAR_THEMES_DIR)
    print("Themes: %s" % Config.CALENDAR_THEMES_DIR)
    print("Images: %s\n" % Config.CALENDAR_IMAGE_DIR)
    print("%-12s %8s  %s" % ("collection", "priority", "rules"))
    for c in collections:
        counts = ", ".join("%d %s" % (len(r), k) for k, r in c.rules.items() if r)
        print("%-12s %8d  %s" % (c.name, c.priority, counts or "-"))
    print("\nRule kind decides first (dates > events > annual > weekdays); priority breaks ties.\n")

    print("=== %d ===" % year)
    day, clashes = date(year, 1, 1), 0
    while day.year == year:
        matches = ct.find_matches(collections, day, Config.DISPLAY_TIMEZONE)
        theme = ct.resolve_theme(collections, day, Config.CALENDAR_IMAGE_DIR, Config.DISPLAY_TIMEZONE)
        # Weekday rules lose every other day by design, so only real clashes are worth showing.
        hidden = [m for m in matches if m.rule != theme.rule and m.kind != "weekdays"]
        clashes += bool(hidden)
        if show_all or hidden or not theme.rule.split(": ")[-1].startswith("weekday"):
            print("%s  %-50s %s" % (day.strftime("%a %d %b"), theme.title or theme.name, theme.rule))
            for m in hidden:
                print("%14s hides %s" % ("", _describe(m, collections)))
        day += timedelta(days=1)
    print("\n%d day(s) with clashes in %d." % (clashes, year))

    # Static checks over every theme, used or not. Problems are logged in the same words the
    # app uses, so each is reported once however many times it was hit.
    used_images = set()
    for coll in collections:
        refs = [(ct.Match(kind, key, ref, coll).rule, ref)
                for kind in ct.RULE_KINDS for key, ref in coll.rules[kind].items()]
        refs += [("%s: theme %s" % (coll.name, name), name) for name in coll.themes]
        if coll.default is not None:
            refs.append(("%s: default" % coll.name, coll.default))
        for rule, ref in refs:
            try:
                theme = ct.build_theme(ref, coll, rule, collections, Config.CALENDAR_IMAGE_DIR)
            except (ValueError, TypeError, KeyError) as exc:
                logging.warning("Calendar themes: %s skipped: %s", rule, exc)
                continue
            if theme.image_path:
                used_images.add(os.path.basename(theme.image_path))
    problems = warnings.messages

    images = sorted(f for f in os.listdir(Config.CALENDAR_IMAGE_DIR) if f.endswith(".png")) \
        if os.path.isdir(Config.CALENDAR_IMAGE_DIR) else []
    unused = [f for f in images if f not in used_images]

    print("\n=== Checks ===")
    for msg in problems:
        print("PROBLEM  %s" % msg)
    for f in unused:
        print("unused   %s" % f)
    if not problems and not unused:
        print("All themes valid; every image is used.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
