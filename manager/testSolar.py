import logging
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, stream_with_context, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import json
import time
import sys
import os
from io import BytesIO
from datetime import datetime, timezone
import requests
from zoneinfo import ZoneInfo
import traceback
import app.images as images
from datetime import timedelta



app = Flask(__name__)



@app.route("/")
def index():
    return "<html><body><h1>Test Solar</h1><img src='/32x32/solar.png' /></body></html>"


@app.route('/32x32/solar.png')
def solar_png():
    """Return a 32x32 solar image with sunrise/sunset times as PNG"""
    try:
        # Create 32x32 image with solar information
        local_zone = ZoneInfo('Europe/London')
        now = datetime.now().astimezone(local_zone)
        now = now.replace(hour=23, minute=40, second=0, microsecond=0)  # Set a fixed time for testing
        sunrise = now.replace(hour=6, minute=12, second=0, microsecond=0)
        sunset = now.replace(hour=18, minute=45, second=0, microsecond=0)
        moonrise = now.replace(hour=20, minute=30, second=0, microsecond=0)
        moonset = now.replace(hour=7, minute=15, second=0, microsecond=0) + timedelta(days=1)  
        solar = {
            "sunrise": sunrise,
            "sunset": sunset,
            "moonrise": moonrise,
            "moonset": moonset,
            "moonPhase": "FULL_MOON",
            "sunrise_hhmm": sunrise.strftime("%H:%M"),
            "sunset_hhmm": sunset.strftime("%H:%M"),
            "moonrise_hhmm": moonrise.strftime("%H:%M"),
            "moonset_hhmm": moonset.strftime("%H:%M"),
        }
        img = images.generate_solar_image(solar, now=now)
        
        png_buffer = BytesIO()
        img.save(png_buffer, format='PNG')
        png_data = png_buffer.getvalue()
        return Response(png_data, mimetype='image/png')
    except Exception as exc:
        traceback.print_exc()
        return Response(str(exc), status=500)

@app.route('/32x32/pride.png')
def pride_png():
    """Return a 32x32 pride flag image with vertical stripes as PNG"""
    try:
        # Create 32x32 image with pride flag colors as vertical stripes
        img = Image.new('RGB', (32, 32), color=(0, 0, 0))
        pixels = img.load()
        
        # Pride flag colors (RGB): Red, Orange, Yellow, Green, Blue, Violet
        pride_colors = [
            (255, 0, 0),      # Red
            (200, 100, 0),    # Orange (darker)
            (255, 255, 0),    # Yellow
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (148, 0, 211)     # Violet
        ]
        
        # Distribute 32 pixels across 6 colors (approximately 5-6 pixels each)
        stripe_width = 32 // 6
        remainder = 32 % 6
        
        x_pos = 0
        for color_idx, color in enumerate(pride_colors):
            # Add extra pixel to first few stripes to account for remainder
            width = stripe_width + (1 if color_idx < remainder else 0)
            for x in range(x_pos, x_pos + width):
                for y in range(32):
                    pixels[x, y] = color
            x_pos += width
        
        png_buffer = BytesIO()
        img.save(png_buffer, format='PNG')
        png_data = png_buffer.getvalue()
        return Response(png_data, mimetype='image/png')
    except Exception as exc:
        return Response(str(exc), status=500)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    app.run(host="0.0.0.0", port=5080, debug=True, use_reloader=False)
