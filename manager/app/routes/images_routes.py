"""Routes serving generated tiles for embedded (Cosmic Unicorn) displays."""
import logging
import os
import traceback
from datetime import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from flask import Blueprint, Response, current_app, request
from PIL import Image

from .. import calendar_themes, images, sensor_tiles


def create_images_blueprint(scheduler, config, sensor_store):
    bp = Blueprint("images", __name__)

    @bp.route("/32x32/home")
    def home():
        image_path = os.path.join(current_app.static_folder, "img", "home.png")
        if not os.path.exists(image_path):
            return Response("File not found", status=404)
        try:
            with Image.open(image_path) as img_file:
                raw, width, height = images.convert_to_brg565(img_file)
            return _brg565_response(raw, width, height)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/weather.png")
    def weather_png():
        weather, _, error = scheduler.get("weather")
        if weather is None:
            return Response(error or "Weather cache warming up", status=503)
        try:
            return _png_response(images.generate_weather_image(weather, isForecast=False))
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/weather.brg565")
    def weather_brg565():
        weather, _, error = scheduler.get("weather")
        if weather is None:
            return Response(error or "Weather cache warming up", status=503)
        try:
            img = images.generate_weather_image(weather, isForecast=False)
            raw, width, height = images.convert_to_brg565(img)
            return _brg565_response(raw, width, height)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/forecast.png")
    def forecast_png():
        forecast, _, error = scheduler.get("forecast")
        if forecast is None:
            return Response(error or "Forecast cache warming up", status=503)
        try:
            return _png_response(images.generate_weather_image(forecast, isForecast=True))
        except Exception as exc:
            traceback.print_exc()
            return Response(str(exc), status=500)

    @bp.route("/32x32/forecast.brg565")
    def forecast_brg565():
        forecast, _, error = scheduler.get("forecast")
        if forecast is None:
            return Response(error or "Forecast cache warming up", status=503)
        try:
            img = images.generate_weather_image(forecast, isForecast=True)
            raw, width, height = images.convert_to_brg565(img)
            return _brg565_response(raw, width, height)
        except Exception as exc:
            return Response(str(exc), status=500)

    # Solar reuses the "forecast" cache (same API call already has sun/moon events) rather than
    # fetching separately.
    @bp.route("/solar.png")
    def solar_png():
        forecast, _, error = scheduler.get("forecast")
        if forecast is None:
            return Response(error or "Forecast cache warming up", status=503)
        try:
            return _png_response(images.generate_solar_image(forecast))
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/solar.brg565")
    def solar_brg565():
        forecast, _, error = scheduler.get("forecast")
        if forecast is None:
            return Response(error or "Forecast cache warming up", status=503)
        try:
            raw, width, height = images.convert_to_brg565(images.generate_solar_image(forecast))
            return _brg565_response(raw, width, height)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/test.brg565")
    def test_brg565():
        try:
            raw, width, height = images.convert_to_brg565(images.generate_test_image())
            return _brg565_response(raw, width, height)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/pride.brg565")
    def pride_brg565():
        try:
            raw, width, height = images.convert_to_brg565(images.generate_pride_image())
            return _brg565_response(raw, width, height)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/pride.png")
    def pride_png():
        try:
            return _png_response(images.generate_pride_image())
        except Exception as exc:
            return Response(str(exc), status=500)

    def _calendar_image():
        """Render today's calendar tile, or the date given as ?date=dd/mm/yyyy (for previewing themes)."""
        requested = request.args.get("date")
        if requested:
            day = datetime.strptime(requested, "%d/%m/%Y").date()
        else:
            day = datetime.now(ZoneInfo(config.DISPLAY_TIMEZONE)).date()
        theme = calendar_themes.resolve_theme(
            calendar_themes.load_collections(config.CALENDAR_THEMES_DIR),
            day,
            config.CALENDAR_IMAGE_DIR,
            config.DISPLAY_TIMEZONE,
        )
        logging.debug("Calendar %s: theme '%s' (%s)", day, theme.name, theme.rule)
        return images.generate_calendar_image(day, theme)

    @bp.route("/32x32/cal.brg565")
    def cal_brg565():
        try:
            raw, width, height = images.convert_to_brg565(_calendar_image())
            return _brg565_response(raw, width, height)
        except ValueError as exc:
            return Response(str(exc), status=400)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/cal.png")
    def cal_png():
        try:
            return _png_response(_calendar_image())
        except ValueError as exc:
            return Response(str(exc), status=400)
        except Exception as exc:
            return Response(str(exc), status=500)

    # Sensor node tiles. Overviews list up to 4 nodes; the per-node variants add a 24h trend.
    # The firmware fetches <server>/32x32/<widget data>, so e.g. data "env/studycosmic.brg565".
    _SENSOR_OVERVIEWS = {
        "env": (sensor_tiles.generate_env_overview, ("temperature", "humidity")),
        "net": (sensor_tiles.generate_net_overview, ("mbps", "rssi")),
        "ping": (sensor_tiles.generate_ping_overview, sensor_tiles.PING_METRICS),
    }
    _SENSOR_DETAILS = {
        "env": sensor_tiles.generate_env_detail,
        "net": sensor_tiles.generate_net_detail,
        "ping": sensor_tiles.generate_ping_detail,
    }

    def _sensor_overview(kind):
        render, metrics = _SENSOR_OVERVIEWS[kind]
        snapshot = sensor_store.snapshot()
        if not any(m in n["latest"] for n in snapshot["nodes"] for m in metrics):
            return None
        return render(snapshot)

    def _sensor_response(img, fmt):
        if img is None:
            return Response("No sensor data yet", status=503)
        if fmt == "png":
            return _png_response(img)
        return _brg565_response(*images.convert_to_brg565(img))

    @bp.route("/32x32/<any(env, net, ping):kind>.<any(brg565, png):fmt>")
    def sensor_overview(kind, fmt):
        try:
            return _sensor_response(_sensor_overview(kind), fmt)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/<any(env, net, ping):kind>/<node_id>.<any(brg565, png):fmt>")
    def sensor_detail(kind, node_id, fmt):
        try:
            img = _SENSOR_DETAILS[kind](sensor_store.snapshot(), node_id)
        except KeyError:
            return Response("Unknown sensor node %s" % node_id, status=404)
        except Exception as exc:
            return Response(str(exc), status=500)
        return _sensor_response(img, fmt)

    def _brg565_response(raw, width, height):
        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(raw)),
            "X-Image-Width": str(width),
            "X-Image-Height": str(height),
        }
        return Response(raw, headers=headers)

    def _png_response(img):
        buf = BytesIO()
        img.save(buf, format="PNG")
        return Response(buf.getvalue(), mimetype="image/png")

    return bp
