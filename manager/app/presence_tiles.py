"""32x32 family presence tile: split screen, home on the left, away on the right.

  rows 0-7    a house icon over the home side  |  a pine tree icon over the away side
  column 16   divider
  rows 9-31   each person's initial at double size (6x10) in their own colour, on the side
              they're on: up to 2 per row and 2 rows per side. Away initials are dimmed.

Someone with no reading yet (gateway not read since start-up) is shown on the away side in grey.
"""
from .images import TILE_SIZE
from .sensor_tiles import NODE_COLORS, _dim, _new_tile, draw_text

DIVIDER_COLOR = (50, 50, 50)
UNKNOWN_COLOR = (90, 90, 90)
AWAY_DIM = 0.6
DIVIDER_X = 16
HALVES = ((0, 16), (17, 15))          # (x start, width) of the home and away sides
LETTER_W, LETTER_H = 6, 10            # 3x5 glyph at scale 2
AREA_TOP = 9                          # people area: rows 9..31, below the icons

# Pixel-art icons: one character per pixel, "." transparent, others looked up in the palette.
HOUSE = (
    "....R....",
    "...RRR...",
    "..RRRRR..",
    ".RRRRRRR.",
    "RRRRRRRRR",
    ".WWWWWWW.",
    ".WWW.WWW.",
    ".WWW.WWW.",
)
TREE = (
    "...G...",
    "..GGG..",
    ".GGGGG.",
    "..GGG..",
    ".GGGGG.",
    "GGGGGGG",
    "...T...",
    "...T...",
)
PALETTE = {
    "R": (220, 60, 40),     # roof
    "W": (230, 200, 150),   # walls (the gap is the door)
    "G": (0, 190, 70),      # foliage
    "T": (150, 85, 30),     # trunk
}


def _draw_icon(pixels, icon, x0, y0):
    for dy, row in enumerate(icon):
        for dx, ch in enumerate(row):
            if ch != ".":
                pixels[x0 + dx, y0 + dy] = PALETTE[ch]


def _slots(count, x0, width):
    """Top-left corners for `count` initials in one half (max 4)."""
    count = min(count, 4)
    if count == 0:
        return []
    area_h = TILE_SIZE - AREA_TOP
    rows = 1 if count <= 2 else 2
    gap_y = (area_h - rows * LETTER_H) // (rows + 1)
    positions = []
    for i in range(count):
        row, col = divmod(i, 2)
        in_row = min(2, count - row * 2)
        gap_x = (width - in_row * LETTER_W) // (in_row + 1)
        x = x0 + gap_x + col * (LETTER_W + gap_x)
        y = AREA_TOP + gap_y + row * (LETTER_H + gap_y)
        positions.append((x, y))
    return positions


def generate_presence_tile(presence):
    img, pixels = _new_tile()
    for y in range(TILE_SIZE):
        pixels[DIVIDER_X, y] = DIVIDER_COLOR
    for icon, (x0, width) in ((HOUSE, HALVES[0]), (TREE, HALVES[1])):
        _draw_icon(pixels, icon, x0 + (width - len(icon[0])) // 2, 0)

    people = presence.get("people", [])
    home = [p for p in people if p.get("home")]
    away = [p for p in people if not p.get("home")]
    for group, (x0, width) in ((home, HALVES[0]), (away, HALVES[1])):
        for person, (x, y) in zip(group, _slots(len(group), x0, width)):
            color = NODE_COLORS[person["slot"] % len(NODE_COLORS)]
            if person.get("home") is None:
                color = UNKNOWN_COLOR
            elif not person["home"]:
                color = _dim(color, AWAY_DIM)
            draw_text(pixels, x, y, person["letter"], color, scale=2)
    return img
