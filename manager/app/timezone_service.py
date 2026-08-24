"""Computes and publishes the configured display timezone's UTC offset, for display clock sync."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo


def utc_offset_minutes(zone_name):
    """Return the offset from UTC for the given IANA zone, in minutes (accounts for DST).

    Uses an explicit zone rather than the process/container's local timezone, since
    containers commonly default to UTC unless deliberately configured otherwise.
    """
    offset = datetime.now(ZoneInfo(zone_name)).utcoffset()
    offmin = int(offset.total_seconds() // 60)
    print(f"Current UTC offset: {offmin} minutes")
    return offmin


def publish_utc_offset(mqtt_service, topic, zone_name):
    """Compute the current UTC offset, publish it as {"tz": <minutes>}, and return it for caching."""
    offset_minutes = utc_offset_minutes(zone_name)
    mqtt_service.publish(topic, json.dumps({"tz": offset_minutes}))
    return offset_minutes
