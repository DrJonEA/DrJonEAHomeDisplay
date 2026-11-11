"""Generate the default day-of-week calendar theme images (Norse / planetary day names).

    Mon - Moon      Tue - Tyr (sword)    Wed - Odin (raven)   Thu - Thor (Mjolnir)
    Fri - Frigg (key, with "Frigg's distaff" - Orion's belt - in the sky)
    Sat - Saturn    Sun - Sun

Each image is 32x22 (the calendar area above the device clock). The default text layout uses
the top row (day of week + date) and the left of the second row (month), so each emblem sits
in the free 12x12 box at the bottom right (x 20-31, y 10-21) over a dark gradient background.

Usage:  python tools/make_calendar_images.py [output_dir]
        (default output_dir: manager/static/img/calendar)
"""
import math
import os
import sys

from PIL import Image

W, H = 32, 22
EMBLEM_X, EMBLEM_Y = 20, 10  # top-left of the 12x12 emblem box

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "img", "calendar")


def gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        color = tuple(round(a + (b - a) * t) for a, b in zip(top, bottom))
        for x in range(W):
            px[x, y] = color
    return img


def plot(img, points, color):
    px = img.load()
    for x, y in points:
        if 0 <= x < W and 0 <= y < H:
            px[x, y] = color


def sprite(img, rows, palette, ox=EMBLEM_X, oy=EMBLEM_Y):
    """Draw an ASCII sprite; '.' is transparent, other chars index `palette`."""
    px = img.load()
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch != ".":
                x, y = ox + dx, oy + dy
                if 0 <= x < W and 0 <= y < H:
                    px[x, y] = palette[ch]


def disc(img, cx, cy, r, color, inside=None):
    """Filled circle; `inside(x, y)` can further restrict which pixels are painted."""
    pts = []
    for y in range(math.floor(cy - r), math.ceil(cy + r) + 1):
        for x in range(math.floor(cx - r), math.ceil(cx + r) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and (inside is None or inside(x, y)):
                pts.append((x, y))
    plot(img, pts, color)


STAR = (200, 200, 230)
DIM_STAR = (90, 90, 130)


# --- Monday: Moon ---------------------------------------------------------------------------
def monday():
    img = gradient((0, 0, 20), (10, 15, 55))
    plot(img, [(14, 1), (7, 10), (17, 12), (12, 20), (30, 9)], DIM_STAR)
    plot(img, [(19, 19), (31, 1)], STAR)
    cx, cy, r = 26, 16, 5.5
    # Crescent: the moon disc minus a disc offset towards the upper left.
    disc(img, cx, cy, r, (235, 235, 210), inside=lambda x, y: (x - (cx - 3)) ** 2 + (y - (cy - 1.5)) ** 2 > r * r)
    return img


# --- Tuesday: Tyr ---------------------------------------------------------------------------
def tuesday():
    img = gradient((30, 0, 0), (85, 12, 8))
    # Tiwaz rune (Tyr's arrow) faintly in the background.
    rune = (110, 30, 25)
    plot(img, [(14, y) for y in range(12, 21)] + [(13, 13), (12, 14), (15, 13), (16, 14)], rune)
    sprite(img, [
        "......W.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        ".....WS.....",
        "..YYYYYYYY..",
        "...y.BB.y...",
        ".....BB.....",
        ".....bB.....",
        "....YYYY....",
    ], {"W": (235, 235, 245), "S": (140, 145, 160), "Y": (230, 180, 40), "y": (150, 110, 20),
        "B": (120, 70, 30), "b": (80, 45, 20)})
    return img


# --- Wednesday: Odin --------------------------------------------------------------------------
def wednesday():
    img = gradient((15, 0, 35), (55, 20, 85))
    plot(img, [(15, 1), (8, 11), (16, 21), (13, 15)], DIM_STAR)
    # Raven perched on a branch, silhouetted against a pale moon.
    disc(img, 26.5, 15, 6.2, (185, 175, 215))
    sprite(img, [
        "............",
        "............",
        "...kkk......",
        "..kWkk......",
        "ggkkkkk.....",
        "...kkkkk....",
        "...kkkkkkk..",
        "....kkkkkkkk",
        "....kkkkkkk.",
        ".....kkk....",
        ".....y.y....",
        "..bbbbbbbbbb",
    ], {"k": (5, 0, 15), "W": (255, 255, 255), "g": (110, 110, 110), "y": (90, 80, 60),
        "b": (110, 70, 35)})
    return img


# --- Thursday: Thor ---------------------------------------------------------------------------
def thursday():
    img = gradient((10, 15, 35), (40, 45, 70))
    sprite(img, [
        "............",
        ".gGGGGGGGGg.",
        ".GGGGGGGGGG.",
        ".GgGgGgGgGG.",
        ".gGGGGGGGGg.",
        ".....BB.....",
        ".....BB.....",
        ".....bB.....",
        ".....BB.....",
        ".....YY.....",
        "....B..B....",
        ".....BB.....",
    ], {"G": (175, 180, 195), "g": (95, 100, 115), "B": (130, 80, 35), "b": (85, 50, 20),
        "Y": (230, 180, 40)}, ox=EMBLEM_X - 2)
    return img


# --- Friday: Frigg ----------------------------------------------------------------------------
def friday():
    img = gradient((0, 25, 30), (10, 60, 55))
    # Frigg's distaff (Orion's belt): three stars in a row.
    plot(img, [(9, 11), (12, 12), (15, 13)], STAR)
    plot(img, [(16, 21), (5, 20)], DIM_STAR)
    sprite(img, [
        "....YYYY....",
        "...Y....Y...",
        "...Y....Y...",
        "...Y....Y...",
        "....yYYy....",
        ".....YY.....",
        ".....Yy.....",
        ".....YY.....",
        ".....YYYY...",
        ".....Yy.....",
        ".....YYYy...",
        ".....YY.....",
    ], {"Y": (240, 200, 70), "y": (160, 120, 30)})
    return img


# --- Saturday: Saturn -------------------------------------------------------------------------
def saturday():
    img = gradient((0, 0, 10), (15, 5, 35))
    plot(img, [(15, 1), (10, 11), (16, 20), (6, 21), (31, 1)], DIM_STAR)
    plot(img, [(14, 14)], STAR)
    cx, cy = 25.5, 15.5
    ring = (200, 170, 120)
    tilt = math.radians(-20)

    def ring_pts(front):
        pts = []
        for i in range(120):
            a = 2 * math.pi * i / 120
            ex, ey = 6.2 * math.cos(a), 2.0 * math.sin(a)
            x = cx + ex * math.cos(tilt) - ey * math.sin(tilt)
            y = cy + ex * math.sin(tilt) + ey * math.cos(tilt)
            if (math.sin(a) > 0) == front:
                pts.append((round(x), round(y)))
        return pts

    plot(img, ring_pts(front=False), ring)
    disc(img, cx, cy, 3.6, (220, 180, 100))
    disc(img, cx, cy, 3.6, (180, 135, 70), inside=lambda x, y: y > cy + 1)  # shaded band
    plot(img, ring_pts(front=True), ring)
    return img


# --- Sunday: Sun ------------------------------------------------------------------------------
def sunday():
    img = gradient((10, 40, 100), (60, 100, 160))
    cx, cy = 26, 16
    rays = []
    for i in range(8):
        a = 2 * math.pi * i / 8
        for d in (5, 6):
            rays.append((round(cx + d * math.cos(a)), round(cy + d * math.sin(a))))
    plot(img, rays, (255, 170, 30))
    disc(img, cx, cy, 3.6, (255, 220, 60))
    plot(img, [(cx - 1, cy - 2), (cx - 2, cy - 1)], (255, 250, 200))  # highlight
    return img


IMAGES = {
    "moon.png": monday,
    "tyr.png": tuesday,
    "odin.png": wednesday,
    "thor.png": thursday,
    "frigg.png": friday,
    "saturn.png": saturday,
    "sun.png": sunday,
}


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else OUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    # Imported here: these modules use this module's helpers.
    from advent_images import ADVENT_IMAGES
    from seasonal_images import SEASONAL_IMAGES
    from tolkien_images import TOLKIEN_IMAGES
    from scifi_images import SCIFI_IMAGES
    from marvel_images import MARVEL_IMAGES
    from midkemia_images import MIDKEMIA_IMAGES
    from dickens_images import DICKENS_IMAGES
    from science_images import SCIENCE_IMAGES
    from doctorwho_images import DOCTORWHO_IMAGES
    images = {**IMAGES, **ADVENT_IMAGES, **SEASONAL_IMAGES, **TOLKIEN_IMAGES, **SCIFI_IMAGES, **MARVEL_IMAGES,
              **MIDKEMIA_IMAGES, **DICKENS_IMAGES, **SCIENCE_IMAGES, **DOCTORWHO_IMAGES}
    for name, make in images.items():
        path = os.path.join(out_dir, name)
        make().save(path)
        print("wrote", path)


if __name__ == "__main__":
    main()
