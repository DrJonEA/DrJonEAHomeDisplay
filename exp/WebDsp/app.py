import logging
import threading
from urllib import response
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify, stream_with_context, send_from_directory
from PIL import Image, ImageDraw, ImageFont
import paho.mqtt.client as mqtt
import json
import time
import sys
import os
from io import BytesIO
from datetime import datetime, timezone
import requests


# Grab environment variables
clientId=os.environ.get("MQTT_CLIENT")
user=os.environ.get("MQTT_USER")
passwd=os.environ.get("MQTT_PASSWD")
host= os.environ.get("MQTT_HOST")
port=int(os.environ.get("MQTT_PORT"))
print("MQTT %s:%d"%(host,port))
if (len(clientId) > 6):
   print("Client: %s..."%clientId[0:4])
else: 
   print("Client: %s..."%clientId)   
if (len(user) > 6):
   print("User: %s..."%user[0:4])
else:
    print("User: %s"%user) 

MQTT_BROKER = host
MQTT_PORT = port
MQTT_TOPIC = "home/display"


app = Flask(__name__)

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id = clientId)
mqtt_client.username_pw_set(username=user, password=passwd)
last_message = {"topic": None, "payload": None, "layout": None, "widgets": None, "version": 0}
message_event = threading.Event()


def on_connect(client, userdata, flags, rc, properties):
    logging.info("MQTT connected: %s", mqtt.connack_string(rc))
    if rc == 0:
        client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    payload = msg.payload.decode(errors="replace")
    logging.info("MQTT message received on %s: %s", msg.topic, payload)
    last_message["topic"] = msg.topic
    last_message["payload"] = payload
    last_message["layout"] = None
    last_message["widgets"] = None

    try:
        parsed = json.loads(payload)
        if isinstance(parsed, dict):
            last_message["layout"] = parsed.get("layout")
            widgets = parsed.get("widgets")
            if isinstance(widgets, list):
                last_message["widgets"] = widgets
    except (json.JSONDecodeError, TypeError):
        pass

    last_message["version"] += 1
    message_event.set()


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message


def mqtt_thread():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    mqtt_client.loop_forever()


def convert_to_brg565(img):
    """Convert a PIL Image to RGB565 format and return raw bytes"""
    img_rgb = img.convert('RGB')
    width, height = img_rgb.size
    pixels = img_rgb.load()
    raw = bytearray()
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            raw.append(rgb565 & 0xFF)
            raw.append((rgb565 >> 8) & 0xFF)
    return bytes(raw), width, height


def generate_calendar_image():
    """Generate a 32x32 calendar image showing day of week, day, and month from system clock"""
    now = datetime.now()
    day = now.day
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_abbr = month_names[now.month - 1]
    dow_abbr = now.strftime("%a")[:2]  # Two letter day of week abbreviation
    
    # Create 32x32 image with black background
    img = Image.new('RGB', (32, 32), color=(0, 0, 0))
    
    # Draw text overlay
    draw = ImageDraw.Draw(img)
    
    # Use bitmap font to avoid antialiasing
    font_small = ImageFont.load_default()
    font_large = ImageFont.load_default()
    
    # Draw day of week and day on same line (top)
    draw.text((2, 2), dow_abbr, font=font_small, fill=(200, 200, 255))
    draw.text((16, 2), "%02d" % day, font=font_large, fill=(255, 255, 255))
    
    # Draw month (below)
    draw.text((2, 14), month_abbr, font=font_large, fill=(255, 255, 50))
    
    return img


def generate_weather_image(lat, lng):
    """Generate a 32x32 weather forecast image with temperature, weather condition, and rain probability"""
    weather = {}
    update(weather, lat, lng)
    
    # Create 32x32 image with black background
    img = Image.new('RGB', (32, 32), color=(0, 0, 0))
    pixels = img.load()
    
    temperature = weather["temperature"]
    rain_probability = weather["precProb"]
    
    # Draw temperature as simple bars (bottom section) with color based on temperature
    temp_color = (255, 100, 0)  # Orange for temperature
    if temperature < 5:
        temp_color = (0, 0, 255)  # Blue for cold
    elif temperature > 25:
        temp_color = (255, 0, 0)  # Red for hot
    elif temperature > 15:
        temp_color = (255, 255, 0)  # Yellow for warm 
    else:
        temp_color = (0, 255, 0)  # Green for mild

    temp_bars = int((temperature / 40) * 8)  # Scale to 0-8 bars
    for i in range(min(temp_bars, 8)):
        for y in range(28, 32):
            pixels[i * 4, y] = temp_color
            pixels[i * 4 + 1, y] = temp_color
            pixels[i * 4 + 2, y] = temp_color

    # Draw rain probability as simple bars (right section) with color based on precipitation type
    percip_color = (100, 150, 255)  # Blue for rain
    if weather["precType"] == "SNOW":
        percip_color = (255, 255, 255)  # White for snow
    elif weather["precType"] == "SLEET":
        percip_color = (200, 200, 255)  # Light blue for sleet 
    elif weather["precType"] == "HAIL":
        percip_color = (150, 150, 255)  # Purple for hail
    elif weather["precType"] == "FREEZING_RAIN":
        percip_color = (0, 0, 255)  # Dark blue for freezing rain
    
    rain_bars = int((rain_probability / 100) * 8)  # Scale to 0-8 bars
    for i in range(min(rain_bars, 8)):
        for x in range(28, 32):
            pixels[x, i * 4] = percip_color
            pixels[x, i * 4 + 1] = percip_color
            pixels[x, i * 4 + 2] = percip_color

    # Paste weather icon
    iconSize = 12
    weather["img"].thumbnail((iconSize, iconSize), Image.Resampling.LANCZOS)
    img.paste(weather["img"], (32 - iconSize, 32 - iconSize))

    # Draw text overlay
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    
    draw.text((0, 0), "%.1fc" % temperature, font=font, fill=(255, 255, 255))
    draw.text((0, 10), "%.1f%%" % weather["humidity"], font=font, fill=(255, 255, 255))

    if weather["precProb"]:
        draw.text((0, 20), "%.1f%%" % weather["precProb"], font=font, fill=(255, 255, 255))
    elif weather["windSpeed"] > 50:
        draw.text((0, 20), "%dkmh" % weather["windSpeed"], font=font, fill=(255, 255, 255))
    
    return img



@app.route("/")
def index():
    return render_template("index.html", message=last_message, topic=MQTT_TOPIC)


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)


@app.route('/32x32/home')
def img():
    image_path = os.path.join(app.root_path, 'static', 'home.png')
    if not os.path.exists(image_path):
        return Response('File not found', status=404)

    try:
        with Image.open(image_path) as img_file:
            img = img_file.convert('RGB')
            width, height = img.size
            pixels = img.load()
            raw = bytearray()
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                    raw.append(rgb565 & 0xFF)
                    raw.append((rgb565 >> 8) & 0xFF)

        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(raw)),
            'X-Image-Width': str(width),
            'X-Image-Height': str(height),
        }
        return Response(bytes(raw), headers=headers)
    except Exception as exc:
        return Response(str(exc), status=500)


@app.route('/weather.png')
def weather_png():
    """Return weather image as PNG"""
    try:
        img = generate_weather_image(50.8, -0.167)  # Brighton coordinates
        png_buffer = BytesIO()
        img.save(png_buffer, format='PNG')
        png_data = png_buffer.getvalue()
        return Response(png_data, mimetype='image/png')
    except Exception as exc:
        return Response(str(exc), status=500)


@app.route('/32x32/weather.brg565')
def weather_brg565():
    """Return weather image in BRG565 format"""
    try:
        img = generate_weather_image(50.8, -0.167)  # Brighton coordinates
        raw, width, height = convert_to_brg565(img)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(raw)),
            'X-Image-Width': str(width),
            'X-Image-Height': str(height),
        }
        return Response(raw, headers=headers)
    except Exception as exc:
        return Response(str(exc), status=500)


@app.route('/32x32/test.brg565')
def test_brg565():
    """Return a 32x32 test image with four colored squares in BRG565 format"""
    try:
        # Create 32x32 image with black background
        img = Image.new('RGB', (32, 32), color=(0, 0, 0))
        pixels = img.load()
        
        # Fill the four quadrants with different colors
        # Top left: Red (16x16)
        for x in range(16):
            for y in range(16):
                pixels[x, y] = (255, 0, 0)
        
        # Top right: Green (16x16)
        for x in range(16, 32):
            for y in range(16):
                pixels[x, y] = (0, 255, 0)
        
        # Bottom left: Blue (16x16)
        for x in range(16):
            for y in range(16, 32):
                pixels[x, y] = (0, 0, 255)
        
        # Bottom right: White (16x16)
        for x in range(16, 32):
            for y in range(16, 32):
                pixels[x, y] = (255, 255, 255)
        
        raw, width, height = convert_to_brg565(img)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(raw)),
            'X-Image-Width': str(width),
            'X-Image-Height': str(height),
        }
        return Response(raw, headers=headers)
    except Exception as exc:
        return Response(str(exc), status=500)


@app.route('/32x32/pride.brg565')
def pride_brg565():
    """Return a 32x32 pride flag image with vertical stripes in BRG565 format"""
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
        
        raw, width, height = convert_to_brg565(img)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(raw)),
            'X-Image-Width': str(width),
            'X-Image-Height': str(height),
        }
        return Response(raw, headers=headers)
    except Exception as exc:
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


@app.route('/32x32/cal.brg565')
def cal_brg565():
    """Return calendar image in BRG565 format"""
    try:
        img = generate_calendar_image()
        raw, width, height = convert_to_brg565(img)
        headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Length': str(len(raw)),
            'X-Image-Width': str(width),
            'X-Image-Height': str(height),
        }
        return Response(raw, headers=headers)
    except Exception as exc:
        return Response(str(exc), status=500)


@app.route('/32x32/cal.png')
def cal_png():
    """Return calendar image as PNG"""
    try:
        img = generate_calendar_image()
        png_buffer = BytesIO()
        img.save(png_buffer, format='PNG')
        png_data = png_buffer.getvalue()
        return Response(png_data, mimetype='image/png')
    except Exception as exc:
        return Response(str(exc), status=500)


@app.route("/publish", methods=["POST"])
def publish():
    topic = request.form.get("topic", MQTT_TOPIC)
    payload = request.form.get("payload", "")
    if payload:
        mqtt_client.publish(topic, payload)
    return redirect(url_for("index"))


@app.route("/latest")
def latest():
    return jsonify({
        "topic": last_message["topic"],
        "payload": last_message["payload"],
        "layout": last_message["layout"],
        "widgets": last_message["widgets"],
        "version": last_message["version"],
    })


@app.route("/events")
def events():
    last_id_header = request.headers.get("Last-Event-ID")
    try:
        last_id = int(last_id_header) if last_id_header else 0
    except ValueError:
        last_id = 0

    @stream_with_context
    def event_stream(last_id):
        while True:
            if last_message["version"] > last_id:
                payload_data = {
                    "topic": last_message["topic"],
                    "payload": last_message["payload"],
                    "layout": last_message["layout"],
                    "widgets": last_message["widgets"],
                    "version": last_message["version"],
                }
                data = json.dumps(payload_data)
                yield f"id: {last_message['version']}\n"
                yield f"data: {data}\n\n"
                last_id = last_message["version"]
            else:
                message_event.wait(timeout=15)
                message_event.clear()
                if last_message["version"] <= last_id:
                    yield ": keep-alive\n\n"

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(event_stream(last_id), headers=headers)


def update(weather, lat, lng):
    a = datetime.now(timezone.utc).timestamp()
    key = os.environ["SMARTCLOCKGOOGLE"]
    url = ("https://weather.googleapis.com/v1/currentConditions:lookup?" +
        "key=%s&location.latitude=%f&location.longitude=%f"%(
            key,
            lat,
            lng
            )
        )
    #print(url)
    x = requests.get(url)
    j = x.json()
    #print(json.dumps(j))

    weather["isDaytime"] = j["isDaytime"]
    weather["temperature"] = j["temperature"]["degrees"]
    weather["text"] = j["weatherCondition"]["description"]["text"]
    weather["type"] = j["weatherCondition"]["type"]
    weather["humidity"] = j["relativeHumidity"]
    weather["windSpeed"] = j["wind"]["speed"]["value"]
    weather["windDir"] = j["wind"]["direction"]["degrees"]
    weather["precProb"] = j["precipitation"]["probability"]["percent"]
    weather["precQnt"] = j["precipitation"]["qpf"]["quantity"]
    weather["precType"] = j["precipitation"]["probability"]["type"]
    weather["icon"] = j["weatherCondition"]["iconBaseUri"]
    response = requests.get(weather["icon"] + "_dark.png")
    weather["img"] = Image.open(BytesIO(response.content))
    weather["updated"] = int(a)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    thread = threading.Thread(target=mqtt_thread, daemon=True)
    thread.start()
    app.run(host="0.0.0.0", port=5080, debug=True, use_reloader=False)
