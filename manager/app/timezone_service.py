"""Computes and publishes the configured display timezone's UTC offset, for display clock sync."""
import json
import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo

# Night window during which the published "blue" tag is sent as true (i.e. night/blue display mode).
NIGHT_START = time(20, 0)
NIGHT_END = time(5, 0)


def utc_offset_minutes(zone_name):
    """Return the offset from UTC for the given IANA zone, in minutes (accounts for DST).

    Uses an explicit zone rather than the process/container's local timezone, since
    containers commonly default to UTC unless deliberately configured otherwise.
    """
    offset = datetime.now(ZoneInfo(zone_name)).utcoffset()
    offmin = int(offset.total_seconds() // 60)
    logging.info("Current UTC offset: %d minutes", offmin)
    return offmin


def _is_blue(local_time):
    """False between 20:00 and 05:00 local time (inclusive of 20:00, exclusive of 05:00), else True."""
    in_night_window = local_time >= NIGHT_START or local_time < NIGHT_END
    return not in_night_window


def publish_utc_offset(mqtt_service, topic, zone_name):
    """Compute the current UTC offset and "blue" flag, publish as {"tz": .., "blue": ..}, and return the offset for caching.

    "blue" is True during the night window (20:00-05:00 local), False during the day.
    """
    offset_minutes = utc_offset_minutes(zone_name)
    blue = not _is_blue(datetime.now(ZoneInfo(zone_name)).time())

    mqtt_service.publish(topic, json.dumps({"tz": offset_minutes, "blue": blue}))
    return offset_minutes
