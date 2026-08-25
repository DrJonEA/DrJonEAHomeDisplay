"""Weather lookup used to render the 32x32 weather tile."""
from datetime import datetime, timezone
from io import BytesIO
from zoneinfo import ZoneInfo

import requests
from PIL import Image


def _parse_utc_timestamp(value):
    """Parse an RFC3339 timestamp (e.g. "2014-10-02T15:01:23Z") into a UTC-aware datetime, or None."""
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _select_moon_time(times, now_utc):
    """Pick the most relevant timestamp from a moonrise/moonset list.

    Google can return more than one moonrise or moonset for a single day (the moon rises/sets
    ~50 min later each day, so a calendar day occasionally contains two of one event, sorted
    ascending). Prefer the most recent one at/before now, else the earliest upcoming one.
    """
    parsed = [t for t in (_parse_utc_timestamp(v) for v in times) if t is not None]
    if not parsed:
        return None
    past = [t for t in parsed if t <= now_utc]
    return max(past) if past else min(parsed)


def fetch_weather(api_key, lat, lng):
    """Query the current-conditions weather API and return a dict of derived fields."""
    url = (
        "https://weather.googleapis.com/v1/currentConditions:lookup?"
        + "key=%s&location.latitude=%f&location.longitude=%f" % (api_key, lat, lng)
    )
    resp = requests.get(url)
    j = resp.json()

    weather = {
        "isDaytime": j["isDaytime"],
        "temperature": j["temperature"]["degrees"],
        "text": j["weatherCondition"]["description"]["text"],
        "type": j["weatherCondition"]["type"],
        "humidity": j["relativeHumidity"],
        "windSpeed": j["wind"]["speed"]["value"],
        "windDir": j["wind"]["direction"]["degrees"],
        "precProb": j["precipitation"]["probability"]["percent"],
        "precQnt": j["precipitation"]["qpf"]["quantity"],
        "precType": j["precipitation"]["probability"]["type"],
        "icon": j["weatherCondition"]["iconBaseUri"],
        "updated": int(datetime.now(timezone.utc).timestamp()),
    }
    icon_resp = requests.get(weather["icon"] + "_dark.png")
    weather["img"] = Image.open(BytesIO(icon_resp.content))
    return weather


def fetch_forecast(api_key, lat, lng, zone_name):
    """Query the current day's forecast (weather, sun/moon events) and return a dict.

    Shaped like fetch_weather's for the temperature/humidity/precipitation fields (reusable by the
    same weather tile renderer), plus sunrise/sunset/moonrise/moonset/moonPhase for the solar tile.
    """
    url = (
        "https://weather.googleapis.com/v1/forecast/days:lookup?"
        + "key=%s&location.latitude=%f&location.longitude=%f&days=1" % (api_key, lat, lng)
    )
    resp = requests.get(url)
    j = resp.json()
    day = j["forecastDays"][0]
    daytime = day["daytimeForecast"]

    local_zone = ZoneInfo(zone_name)
    sun_events = day.get("sunEvents", {})
    moon_events = day.get("moonEvents", {})
    now_utc = datetime.now(timezone.utc)

    sunrise = _parse_utc_timestamp(sun_events.get("sunriseTime"))
    sunset = _parse_utc_timestamp(sun_events.get("sunsetTime"))
    moonrise = _select_moon_time(moon_events.get("moonriseTimes") or [], now_utc)
    moonset = _select_moon_time(moon_events.get("moonsetTimes") or [], now_utc)

    sunrise = sunrise.astimezone(local_zone) if sunrise else None
    sunset = sunset.astimezone(local_zone) if sunset else None
    moonrise = moonrise.astimezone(local_zone) if moonrise else None
    moonset = moonset.astimezone(local_zone) if moonset else None

    #print(f"Sunrise: {sunrise}, Sunset: {sunset}, Moonrise: {moonrise}, Moonset: {moonset}" )
    forecast = {
        "temperature": day["maxTemperature"]["degrees"],
        "tempMin": day["minTemperature"]["degrees"],
        "text": daytime["weatherCondition"]["description"]["text"],
        "type": daytime["weatherCondition"]["type"],
        "humidity": daytime["relativeHumidity"],
        "windSpeed": daytime["wind"]["speed"]["value"],
        "precProb": daytime["precipitation"]["probability"]["percent"],
        # Precise local datetimes power the solar tile's sun/moon arc position; the _hhmm
        # strings are the cached hour:minute-only values for anything that just needs a time.
        "sunrise": sunrise,
        "sunset": sunset,
        "moonrise": moonrise,
        "moonset": moonset,
        "sunrise_hhmm": sunrise.strftime("%H:%M") if sunrise else None,
        "sunset_hhmm": sunset.strftime("%H:%M") if sunset else None,
        "moonrise_hhmm": moonrise.strftime("%H:%M") if moonrise else None,
        "moonset_hhmm": moonset.strftime("%H:%M") if moonset else None,
        "moonPhase": moon_events.get("moonPhase"),
        "precType": daytime["precipitation"]["probability"]["type"],
        "icon": daytime["weatherCondition"]["iconBaseUri"],
        "updated": int(datetime.now(timezone.utc).timestamp()),
    }
    icon_resp = requests.get(forecast["icon"] + "_dark.png")
    forecast["img"] = Image.open(BytesIO(icon_resp.content))
    return forecast
