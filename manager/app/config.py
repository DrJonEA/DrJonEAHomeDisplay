"""Environment-derived configuration for the display manager."""
import os

_MANAGER_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Config:
    MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT")
    MQTT_USER = os.environ.get("MQTT_USER")
    MQTT_PASSWD = os.environ.get("MQTT_PASSWD")
    MQTT_HOST = os.environ.get("MQTT_HOST")
    MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
    MQTT_TOPIC = "drjonea/display"
    # Sensor nodes publish readings here (see app/sensor_store.py)
    SENSOR_TOPIC = os.environ.get("SENSOR_TOPIC", "drjonea/sensor/#")
    # External network view from a UniFi gateway (see app/unifi.py). Disabled unless an API key
    # or a local username/password is set.
    UNIFI_HOST = os.environ.get("UNIFI_HOST", "192.168.1.1")
    UNIFI_SITE = os.environ.get("UNIFI_SITE", "default")
    UNIFI_API_KEY = os.environ.get("UNIFI_API_KEY")
    UNIFI_USER = os.environ.get("UNIFI_USER")
    UNIFI_PASSWD = os.environ.get("UNIFI_PASSWD")
    UNIFI_CA_FILE = os.environ.get("UNIFI_CA_FILE")
    # Family presence (see app/presence.py): people and their devices. Needs the UniFi settings.
    PRESENCE_FILE = os.environ.get("PRESENCE_FILE", os.path.join(_MANAGER_DIR, "presence.json"))
    # DEFCON status sent to the displays (see app/defcon.py). 5 is all well; never below MIN.
    DEFCON_INTERVAL_SECONDS = int(os.environ.get("DEFCON_INTERVAL_SECONDS", "30"))
    DEFCON_MIN_LEVEL = int(os.environ.get("DEFCON_MIN_LEVEL", "2"))
    DEFCON_SLOW_LATENCY_MS = float(os.environ.get("DEFCON_SLOW_LATENCY_MS", "80"))
    DEFCON_SLOW_DOWN_MBPS = float(os.environ.get("DEFCON_SLOW_DOWN_MBPS", "250"))
    DEFCON_SLOW_UP_MBPS = float(os.environ.get("DEFCON_SLOW_UP_MBPS", "25"))
    # Pinged locally only if the gateway's own internet monitors can't be read
    WAN_PING_TARGETS = [t.strip() for t in os.environ.get(
        "WAN_PING_TARGETS", "www.google.com,www.microsoft.com,1.1.1.1,aws.amazon.com").split(",") if t.strip()]
    WEATHER_API_KEY = os.environ.get("SMARTCLOCKGOOGLE")
    # Default location used for generated weather tiles (Brighton, UK)
    WEATHER_LAT = float(os.environ.get("WEATHER_LAT", "50.8"))
    WEATHER_LNG = float(os.environ.get("WEATHER_LNG", "-0.167"))
    # IANA zone used for the published TZ offset; independent of the host/container OS timezone
    DISPLAY_TIMEZONE = os.environ.get("DISPLAY_TIMEZONE", "Europe/London")
    # Calendar tile themes (see app/calendar_themes.py) and the directory holding their images
    CALENDAR_THEMES_DIR = os.environ.get(
        "CALENDAR_THEMES_DIR", os.path.join(_MANAGER_DIR, "calendar_themes")
    )
    CALENDAR_IMAGE_DIR = os.environ.get(
        "CALENDAR_IMAGE_DIR", os.path.join(_MANAGER_DIR, "static", "img", "calendar")
    )


def masked(value, keep=4):
    """Return a value with all but the first `keep` characters hidden, for safe logging."""
    if not value:
        return value
    if len(value) <= keep:
        return value
    return value[:keep] + "..."
