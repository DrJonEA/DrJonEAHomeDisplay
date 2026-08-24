"""Environment-derived configuration for the display manager."""
import os


class Config:
    MQTT_CLIENT_ID = os.environ.get("MQTT_CLIENT")
    MQTT_USER = os.environ.get("MQTT_USER")
    MQTT_PASSWD = os.environ.get("MQTT_PASSWD")
    MQTT_HOST = os.environ.get("MQTT_HOST")
    MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
    MQTT_TOPIC = "home/display"
    WEATHER_API_KEY = os.environ.get("SMARTCLOCKGOOGLE")
    # Default location used for generated weather tiles (Brighton, UK)
    WEATHER_LAT = float(os.environ.get("WEATHER_LAT", "50.8"))
    WEATHER_LNG = float(os.environ.get("WEATHER_LNG", "-0.167"))
    # IANA zone used for the published TZ offset; independent of the host/container OS timezone
    DISPLAY_TIMEZONE = os.environ.get("DISPLAY_TIMEZONE", "Europe/London")


def masked(value, keep=4):
    """Return a value with all but the first `keep` characters hidden, for safe logging."""
    if not value:
        return value
    if len(value) <= keep:
        return value
    return value[:keep] + "..."
