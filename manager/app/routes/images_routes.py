"""Routes serving generated tiles for embedded (Cosmic Unicorn) displays."""
import os
from io import BytesIO

from flask import Blueprint, Response, current_app
from PIL import Image

from .. import images


def create_images_blueprint(scheduler):
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
            return _png_response(images.generate_weather_image(weather, badge_color=images.CURRENT_BADGE_COLOR))
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/weather.brg565")
    def weather_brg565():
        weather, _, error = scheduler.get("weather")
        if weather is None:
            return Response(error or "Weather cache warming up", status=503)
        try:
            img = images.generate_weather_image(weather, badge_color=images.CURRENT_BADGE_COLOR)
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
            return _png_response(images.generate_weather_image(forecast, badge_color=images.FORECAST_BADGE_COLOR))
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/forecast.brg565")
    def forecast_brg565():
        forecast, _, error = scheduler.get("forecast")
        if forecast is None:
            return Response(error or "Forecast cache warming up", status=503)
        try:
            img = images.generate_weather_image(forecast, badge_color=images.FORECAST_BADGE_COLOR)
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

    @bp.route("/32x32/cal.brg565")
    def cal_brg565():
        try:
            raw, width, height = images.convert_to_brg565(images.generate_calendar_image())
            return _brg565_response(raw, width, height)
        except Exception as exc:
            return Response(str(exc), status=500)

    @bp.route("/32x32/cal.png")
    def cal_png():
        try:
            return _png_response(images.generate_calendar_image())
        except Exception as exc:
            return Response(str(exc), status=500)

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
