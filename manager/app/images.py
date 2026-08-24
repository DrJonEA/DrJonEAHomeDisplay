"""32x32 tile generation for embedded (Cosmic Unicorn) displays, plus BRG565 conversion."""
import math
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

TILE_SIZE = 32
BADGE_SIZE = 6
# Corner badge colors so current-conditions and forecast tiles are visually distinguishable at a glance.
CURRENT_BADGE_COLOR = (79, 216, 255)
FORECAST_BADGE_COLOR = (255, 201, 77)

# Solar tile: sun path (top half) and moon path (bottom half), split at the horizon row.
HORIZON_Y = TILE_SIZE // 2
ARC_HEIGHT = HORIZON_Y - 3
DISK_RADIUS = 3
SUN_COLOR = (255, 200, 60)
MOON_LIT_COLOR = (225, 225, 235)
MOON_DARK_COLOR = (35, 35, 55)
SOLAR_FONT_SIZE = 8
# Illumination fraction and lit side (True = right, waxing) per Google's MoonPhase enum.
MOON_PHASE_ILLUMINATION = {
    "NEW_MOON": (0.0, True),
    "WAXING_CRESCENT": (0.25, True),
    "FIRST_QUARTER": (0.5, True),
    "WAXING_GIBBOUS": (0.75, True),
    "FULL_MOON": (1.0, True),
    "WANING_GIBBOUS": (0.75, False),
    "LAST_QUARTER": (0.5, False),
    "WANING_CRESCENT": (0.25, False),
}


def convert_to_brg565(img):
    """Convert a PIL Image to RGB565 format and return raw bytes."""
    img_rgb = img.convert("RGB")
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
    """Generate a 32x32 calendar tile showing day of week, day, and month from system clock."""
    now = datetime.now()
    day = now.day
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_abbr = month_names[now.month - 1]
    dow_abbr = now.strftime("%a")[:2]

    img = Image.new("RGB", (TILE_SIZE, TILE_SIZE), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font_small = ImageFont.load_default()
    font_large = ImageFont.load_default()

    draw.text((2, 2), dow_abbr, font=font_small, fill=(200, 200, 255))
    draw.text((16, 2), "%02d" % day, font=font_large, fill=(255, 255, 255))
    draw.text((2, 14), month_abbr, font=font_large, fill=(255, 255, 50))

    return img


def generate_weather_image(weather, badge_color=None):
    """Generate a 32x32 weather forecast tile from an already-fetched weather dict (see weather.fetch_weather).

    badge_color, if given, is painted as a small top-right corner square (e.g. CURRENT_BADGE_COLOR
    vs FORECAST_BADGE_COLOR) so otherwise-identical current/forecast tiles can be told apart.
    """
    img = Image.new("RGB", (TILE_SIZE, TILE_SIZE), color=(0, 0, 0))
    pixels = img.load()

    temperature = weather["temperature"]
    rain_probability = weather["precProb"]

    if temperature < 5:
        temp_color = (0, 0, 255)
    elif temperature > 25:
        temp_color = (255, 0, 0)
    elif temperature > 15:
        temp_color = (255, 255, 0)
    else:
        temp_color = (0, 255, 0)

    temp_bars = int((temperature / 40) * 8)
    for i in range(min(temp_bars, 8)):
        for y in range(28, 32):
            pixels[i * 4, y] = temp_color
            pixels[i * 4 + 1, y] = temp_color
            pixels[i * 4 + 2, y] = temp_color

    percip_color = (100, 150, 255)
    if weather["precType"] == "SNOW":
        percip_color = (255, 255, 255)
    elif weather["precType"] == "SLEET":
        percip_color = (200, 200, 255)
    elif weather["precType"] == "HAIL":
        percip_color = (150, 150, 255)
    elif weather["precType"] == "FREEZING_RAIN":
        percip_color = (0, 0, 255)

    rain_bars = int((rain_probability / 100) * 8)
    for i in range(min(rain_bars, 8)):
        for x in range(28, 32):
            pixels[x, i * 4] = percip_color
            pixels[x, i * 4 + 1] = percip_color
            pixels[x, i * 4 + 2] = percip_color

    icon_size = 12
    icon = weather["img"].copy()
    icon.thumbnail((icon_size, icon_size), Image.Resampling.LANCZOS)
    img.paste(icon, (TILE_SIZE - icon_size, TILE_SIZE - icon_size))

    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.text((0, 0), "%.1fc" % temperature, font=font, fill=(255, 255, 255))
    draw.text((0, 10), "%.1f%%" % weather["humidity"], font=font, fill=(255, 255, 255))

    if weather["precProb"]:
        draw.text((0, 20), "%d%%" % int(weather["precProb"]), font=font, fill=(255, 255, 255))
    elif weather["windSpeed"] > 50:
        draw.text((0, 20), "%dkmh" % weather["windSpeed"], font=font, fill=(255, 255, 255))

    if badge_color:
        for x in range(TILE_SIZE - BADGE_SIZE, TILE_SIZE):
            for y in range(BADGE_SIZE):
                pixels[x, y] = badge_color

    return img


def generate_test_image():
    """Return a 32x32 test tile with four colored quadrants."""
    img = Image.new("RGB", (TILE_SIZE, TILE_SIZE), color=(0, 0, 0))
    pixels = img.load()
    quadrants = [
        (range(0, 16), range(0, 16), (255, 0, 0)),
        (range(16, 32), range(0, 16), (0, 255, 0)),
        (range(0, 16), range(16, 32), (0, 0, 255)),
        (range(16, 32), range(16, 32), (255, 255, 255)),
    ]
    for xs, ys, color in quadrants:
        for x in xs:
            for y in ys:
                pixels[x, y] = color
    return img


def generate_pride_image():
    """Return a 32x32 tile with pride-flag vertical stripes."""
    img = Image.new("RGB", (TILE_SIZE, TILE_SIZE), color=(0, 0, 0))
    pixels = img.load()

    pride_colors = [
        (255, 0, 0),
        (200, 100, 0),
        (255, 255, 0),
        (0, 255, 0),
        (0, 0, 255),
        (148, 0, 211),
    ]
    stripe_width = TILE_SIZE // len(pride_colors)
    remainder = TILE_SIZE % len(pride_colors)

    x_pos = 0
    for color_idx, color in enumerate(pride_colors):
        width = stripe_width + (1 if color_idx < remainder else 0)
        for x in range(x_pos, x_pos + width):
            for y in range(TILE_SIZE):
                pixels[x, y] = color
        x_pos += width

    return img


def _rise_set_fraction(rise, set_, now):
    """Return 0..1 progress from rise to set at time `now`, or None if either is missing or now is outside the window."""
    if rise is None or set_ is None or now < rise or now > set_:
        return None
    span = (set_ - rise).total_seconds()
    if span <= 0:
        return None
    return (now - rise).total_seconds() / span


def _arc_point(fraction, direction):
    """Position along a rise-to-set arc: x sweeps left-to-right, y arcs away from the horizon (direction -1/+1)."""
    x = round(fraction * (TILE_SIZE - 1))
    y = round(HORIZON_Y + direction * ARC_HEIGHT * math.sin(math.pi * fraction))
    return x, y


def _fill_disk(pixels, cx, cy, radius, min_y, max_y, color_fn):
    """Paint a filled circle, clipped to the tile and to the [min_y, max_y] half of the screen.

    Clipping to one half is what makes a disk centered on the horizon (rise/set) render as
    just its partial, rising/setting sliver.
    """
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx * dx + dy * dy > radius * radius:
                continue
            x, y = cx + dx, cy + dy
            if not (0 <= x < TILE_SIZE and min_y <= y <= max_y):
                continue
            pixels[x, y] = color_fn(dx)


def generate_solar_image(solar):
    """Generate a 32x32 tile: today's sun path (top half) and moon path (bottom half).

    Positions come from an already-fetched forecast dict (see weather.fetch_forecast) with
    sunrise/sunset/moonrise/moonset datetimes and moonPhase. The moon disk is shaded to reflect
    the current phase (which side is lit and by how much).
    """
    img = Image.new("RGB", (TILE_SIZE, TILE_SIZE), color=(0, 0, 0))
    pixels = img.load()

    sunrise, sunset = solar.get("sunrise"), solar.get("sunset")
    moonrise, moonset = solar.get("moonrise"), solar.get("moonset")

    reference_tz = next((t.tzinfo for t in (sunrise, sunset, moonrise, moonset) if t is not None), None)
    now = datetime.now(reference_tz) if reference_tz else datetime.now()

    sun_fraction = _rise_set_fraction(sunrise, sunset, now)
    if sun_fraction is not None:
        cx, cy = _arc_point(sun_fraction, direction=-1)
        _fill_disk(pixels, cx, cy, DISK_RADIUS, min_y=0, max_y=HORIZON_Y - 1, color_fn=lambda dx: SUN_COLOR)

    moon_fraction = _rise_set_fraction(moonrise, moonset, now)
    if moon_fraction is not None:
        cx, cy = _arc_point(moon_fraction, direction=1)
        illum_fraction, waxing = MOON_PHASE_ILLUMINATION.get(solar.get("moonPhase"), (1.0, True))

        def moon_color(dx, illum=illum_fraction, waxing=waxing):
            # Bin pixels to the middle of their slot (not the edge) so illum=0/1 don't land exactly
            # on the >=/<= boundary and light up (or leave dark) a stray edge column.
            u = (dx + DISK_RADIUS + 0.5) / (2 * DISK_RADIUS + 1)
            lit = (u >= (1 - illum)) if waxing else (u <= illum)
            return MOON_LIT_COLOR if lit else MOON_DARK_COLOR

        _fill_disk(pixels, cx, cy, DISK_RADIUS, min_y=HORIZON_Y, max_y=TILE_SIZE - 1, color_fn=moon_color)

    # Drawn last (on top of the disks) so the times stay legible even if the sun disk is nearby.
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default(size=SOLAR_FONT_SIZE)
    sunrise_label = solar.get("sunrise_hhmm")
    sunset_label = solar.get("sunset_hhmm")
    if sunrise_label:
        draw.text((5, 8), sunrise_label, font=font, fill=SUN_COLOR)
    if sunset_label:
        text_width = draw.textlength(sunset_label, font=font)
        draw.text((5, 16), sunset_label, font=font, fill=SUN_COLOR)

    return img
