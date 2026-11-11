"""Dates of moveable calendar events: Easter, equinoxes and solstices.

Equinox/solstice instants use Meeus, "Astronomical Algorithms" ch. 27 (valid 1000-3000 AD,
accurate to about a minute), then are converted to the display timezone, since an event late
in the evening UTC can fall on the next local day elsewhere. Easter is the Gregorian
(Western) date via the anonymous Gregorian computus.
"""
import math
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

# Table 27.B (years 2000-3000): mean JDE coefficients for each event, in powers of Y.
_MEAN_JDE = {
    "march_equinox": (2451623.80984, 365242.37404, 0.05169, -0.00411, -0.00057),
    "june_solstice": (2451716.56767, 365241.62603, 0.00325, 0.00888, -0.00030),
    "september_equinox": (2451810.21715, 365242.01767, -0.11575, 0.00337, 0.00078),
    "december_solstice": (2451900.05952, 365242.74049, -0.06223, -0.00823, 0.00032),
}

# Table 27.C: periodic terms (A, B degrees, C degrees/century).
_PERIODIC = [
    (485, 324.96, 1934.136), (203, 337.23, 32964.467), (199, 342.08, 20.186),
    (182, 27.85, 445267.112), (156, 73.14, 45036.886), (136, 171.52, 22518.443),
    (77, 222.54, 65928.934), (74, 296.72, 3034.906), (70, 243.58, 9037.513),
    (58, 119.81, 33718.147), (52, 297.17, 150.678), (50, 21.02, 2281.226),
    (45, 247.54, 29929.562), (44, 325.15, 31555.956), (29, 60.93, 4443.417),
    (18, 155.12, 67555.328), (17, 288.79, 4562.452), (16, 198.04, 62894.029),
    (14, 199.76, 31436.921), (12, 95.39, 14577.848), (12, 287.11, 31931.756),
    (12, 320.81, 34777.259), (9, 227.73, 1222.114), (8, 15.45, 16859.074),
]

_JD_UNIX_EPOCH = 2440587.5


def season_instant(year, event):
    """UTC datetime of an equinox/solstice (`event` is a key of _MEAN_JDE). TT-UTC (~70s) is ignored."""
    y = (year - 2000) / 1000
    c = _MEAN_JDE[event]
    jde0 = c[0] + c[1] * y + c[2] * y ** 2 + c[3] * y ** 3 + c[4] * y ** 4
    t = (jde0 - 2451545.0) / 36525
    w = math.radians(35999.373 * t - 2.47)
    dlambda = 1 + 0.0334 * math.cos(w) + 0.0007 * math.cos(2 * w)
    s = sum(a * math.cos(math.radians(b + cc * t)) for a, b, cc in _PERIODIC)
    jde = jde0 + 0.00001 * s / dlambda
    return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(days=jde - _JD_UNIX_EPOCH)


def easter(year):
    """Western (Gregorian) Easter Sunday."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return date(year, month, day + 1)


@lru_cache(maxsize=32)
def events_for_year(year, zone_name="UTC"):
    """Map of event name -> local date for `year`.

    Season names are northern-hemisphere (spring = March equinox); the month-based aliases
    (march_equinox etc.) are also available.
    """
    zone = ZoneInfo(zone_name)
    seasons = {name: season_instant(year, name).astimezone(zone).date() for name in _MEAN_JDE}
    return {
        "easter": easter(year),
        **seasons,
        "spring_equinox": seasons["march_equinox"],
        "summer_solstice": seasons["june_solstice"],
        "autumn_equinox": seasons["september_equinox"],
        "winter_solstice": seasons["december_solstice"],
    }


EVENT_NAMES = frozenset(events_for_year(2000))
