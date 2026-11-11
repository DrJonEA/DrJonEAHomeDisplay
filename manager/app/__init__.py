"""Flask application factory for the display manager."""
import os

from flask import Flask

from .config import Config
from .display_presets import DISPLAY_TOPIC, get_preset, preset_payload_json
from .mqtt_service import MqttService
from .routes.api import create_api_blueprint
from .routes.images_routes import create_images_blueprint
from .routes.pages import create_pages_blueprint
from .scheduler import DataScheduler
from .timezone_service import publish_utc_offset
from .weather import fetch_forecast, fetch_weather

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEATHER_SCHEDULE_MINUTES = [0, 15, 30, 45]
FORECAST_SCHEDULE_MINUTES = [0, 30]
TZ_CHECK_SCHEDULE_MINUTES = list(range(60))

# Independent schedules for re-announcing (re-publishing) a preset over MQTT, regardless of
# whether the underlying cached data changed - e.g. so a display that missed/rebooted stays in sync.
WEATHER_ANNOUNCE_MINUTES = list(range(5, 60, 5))
FORECAST_ANNOUNCE_MINUTES = list(range(1, 60, 5))
SOLAR_ANNOUNCE_MINUTES = [3, 18, 33, 48]
CALENDAR_ANNOUNCE_MINUTES = [0]


def create_app(config=None):
    config = config or Config()
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )

    mqtt_service = MqttService(config)
    app.mqtt_service = mqtt_service

    weather_preset = get_preset("weather")

    def fetch_and_announce_weather():
        weather = fetch_weather(config.WEATHER_API_KEY, config.WEATHER_LAT, config.WEATHER_LNG)
        # Push the weather preset so displays switch to/refresh the weather tile whenever the cache updates.
        mqtt_service.publish(DISPLAY_TOPIC, preset_payload_json(weather_preset))
        return weather

    scheduler = DataScheduler()
    scheduler.register("weather", fetch_and_announce_weather, WEATHER_SCHEDULE_MINUTES)
    scheduler.register(
        "forecast",
        lambda: fetch_forecast(config.WEATHER_API_KEY, config.WEATHER_LAT, config.WEATHER_LNG, config.DISPLAY_TIMEZONE),
        FORECAST_SCHEDULE_MINUTES,
    )
    scheduler.register(
        "tz_offset",
        lambda: publish_utc_offset(mqtt_service, DISPLAY_TOPIC, config.DISPLAY_TIMEZONE),
        TZ_CHECK_SCHEDULE_MINUTES,
    )

    def announce(preset_key):
        mqtt_service.publish(DISPLAY_TOPIC, preset_payload_json(get_preset(preset_key)))
        return preset_key

    scheduler.register("announce_weather", lambda: announce("weather"), WEATHER_ANNOUNCE_MINUTES)
    scheduler.register("announce_forecast", lambda: announce("forecast"), FORECAST_ANNOUNCE_MINUTES)
    scheduler.register("announce_solar", lambda: announce("solar"), SOLAR_ANNOUNCE_MINUTES)
    scheduler.register("announce_calendar", lambda: announce("calendar"), CALENDAR_ANNOUNCE_MINUTES)
    # Future sources (sunrise/sunset, moonrise/moonset) register here the same way.
    app.scheduler = scheduler

    app.register_blueprint(create_pages_blueprint(mqtt_service))
    app.register_blueprint(create_api_blueprint(mqtt_service))
    app.register_blueprint(create_images_blueprint(scheduler, config))

    return app
