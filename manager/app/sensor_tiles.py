"""32x32 tiles visualising sensor node data (see sensor_store.SensorStore.snapshot).

Overview tiles show up to four nodes, one 8px row each, led by a stripe in the node's
fixed colour. Detail tiles show one node's readings plus a 24h trend line.

Numbers use a hand-drawn 3x5 pixel font: TrueType fonts at this size blur or merge
glyphs on the LED matrix, while 3x5 keeps "20.0" to 13px wide and pin sharp.
"""
import time

from PIL import Image

from .images import TILE_SIZE

ROW_HEIGHT = 8
MAX_ROWS = TILE_SIZE // ROW_HEIGHT
STRIPE_WIDTH = 2
# Overview rows: stripe (x0-1) | node letter (x3-5) | values from x7.
LETTER_X = STRIPE_WIDTH + 1
VALUE_X = LETTER_X + 4
MIN_VALUE_GAP = 2           # between a row's left and right-aligned values


def _fits(left_text, right_text):
    return VALUE_X + text_width(left_text) + MIN_VALUE_GAP + text_width(right_text) <= 32
TREND_TOP = 21          # detail tiles: trend line occupies rows 21..31
TREND_SECONDS = 24 * 60 * 60

# Node identity colours, in fixed order of first appearance (validated categorical palette).
NODE_COLORS = [
    (0x39, 0x87, 0xE5), (0xD9, 0x59, 0x26), (0x19, 0x9E, 0x70), (0xC9, 0x85, 0x00),
    (0xD5, 0x51, 0x81), (0x00, 0x83, 0x00), (0x90, 0x85, 0xE9), (0xE6, 0x67, 0x67),
]
MISSING_COLOR = (90, 90, 90)
STALE_DIM = 0.5
TEXT_COLOR = (255, 255, 255)
SIGNAL_OFF_COLOR = (40, 40, 40)
TREND_NET_COLOR = (0, 200, 255)
# Net tiles: ping blocks sit between the Mbps figure (ends by x=14) and the signal bars (x=25).
PING_BLOCKS_X = 16          # net node tile
NET_ROW_BLOCKS_X = 19       # net overview rows: narrower blocks between Mbps and signal bars
PING_METRICS = ("icmp_ms", "icmp_loss", "mqtt_ms", "mqtt_loss")

# 3x5 glyphs, one string of 3 bits per row ('.' is a single column).
_GLYPHS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "001", "001", "001"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    "-": ("000", "000", "111", "000", "000"),
    "%": ("101", "001", "010", "100", "101"),
    ".": ("0", "0", "0", "0", "1"),
    # Arrows and A-Z: WAN tile target labels, presence tile names and HOME/AWAY.
    "↓": ("010", "010", "010", "111", "010"),
    "↑": ("010", "111", "010", "010", "010"),
    "A": ("010", "101", "111", "101", "101"),
    "C": ("111", "100", "100", "100", "111"),
    "F": ("111", "100", "110", "100", "100"),
    "G": ("111", "100", "101", "101", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "Q": ("111", "101", "101", "111", "001"),
    "U": ("101", "101", "101", "101", "111"),
    "B": ("110", "101", "110", "101", "110"),
    "D": ("110", "101", "101", "101", "110"),
    "E": ("111", "100", "110", "100", "111"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "J": ("001", "001", "001", "101", "010"),
    "K": ("101", "101", "110", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "N": ("110", "101", "101", "101", "101"),
    "O": ("111", "101", "101", "101", "111"),
    "P": ("110", "101", "110", "100", "100"),
    "R": ("110", "101", "110", "101", "101"),
    "S": ("011", "100", "010", "001", "110"),
    "T": ("111", "010", "010", "010", "010"),
    "V": ("101", "101", "101", "101", "010"),
    "W": ("101", "101", "111", "111", "101"),
    "X": ("101", "101", "010", "101", "101"),
    "Y": ("101", "101", "010", "010", "010"),
    "Z": ("111", "001", "010", "100", "111"),
    "?": ("111", "001", "010", "000", "010"),
}
GLYPH_HEIGHT = 5


def text_width(text, scale=1):
    widths = [len(_GLYPHS[ch][0]) * scale for ch in text]
    return sum(widths) + scale * max(len(widths) - 1, 0)


def draw_text(pixels, x, y, text, color, scale=1):
    """Draw `text` with the 3x5 font at (x, y); returns the width drawn. Clips to the tile."""
    start = x
    for ch in text:
        rows = _GLYPHS[ch]
        for gy, row in enumerate(rows):
            for gx, bit in enumerate(row):
                if bit != "1":
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        px, py = x + gx * scale + sx, y + gy * scale + sy
                        if 0 <= px < TILE_SIZE and 0 <= py < TILE_SIZE:
                            pixels[px, py] = color
        x += (len(rows[0]) + 1) * scale
    return x - start - scale


def temperature_color(c):
    """Indoor-oriented scale: cold blue, cool cyan, comfortable green, warm yellow, hot red."""
    if c < 16:
        return (60, 110, 255)
    if c < 19:
        return (0, 200, 255)
    if c < 24:
        return (0, 255, 80)
    if c < 27:
        return (255, 210, 0)
    return (255, 40, 40)


def humidity_color(h):
    if h < 30:
        return (255, 170, 0)     # dry
    if h <= 60:
        return (0, 200, 255)     # comfortable
    return (60, 110, 255)        # damp


# Round-trip colour bands (ms): green below the first, yellow below the second, red above.
# ICMP is the bare network trip. MQTT goes via the broker and the firmware's ping task, and
# normally takes ~800 ms, so it gets its own, much wider bands.
LATENCY_BANDS = {
    "icmp": (50, 200),
    "mqtt": (500, 1200),
    "internet": (30, 80),   # ISP and cloud round trips
}


def latency_color(ms, kind="icmp"):
    fast, slow = LATENCY_BANDS[kind]
    if ms < fast:
        return (0, 255, 80)
    if ms < slow:
        return (255, 210, 0)
    return (255, 40, 40)


def signal_level(rssi):
    """WiFi RSSI (dBm) to 0-4 bars."""
    for level, floor in ((4, -55), (3, -67), (2, -75), (1, -85)):
        if rssi >= floor:
            return level
    return 0


_SIGNAL_COLORS = {4: (0, 255, 80), 3: (0, 255, 80), 2: (255, 210, 0), 1: (255, 40, 40), 0: (255, 40, 40)}


def _dim(color, factor):
    return tuple(int(c * factor) for c in color)


def _node_color(node):
    color = NODE_COLORS[node["slot"] % len(NODE_COLORS)]
    return _dim(color, STALE_DIM) if node["stale"] else color


def _fmt_temp(c):
    return "--" if c is None else "%.1f" % c


def _fmt_hum(h):
    return "--" if h is None else "%d" % round(min(max(h, 0), 99))


def _fmt_mbps(m):
    if m is None:
        return "--"
    return "%.1f" % m if m < 10 else "%d" % round(m)


LOST_COLOR = (255, 40, 40)


def _probe_color(node, kind, unmeasured=MISSING_COLOR):
    """Latency colour for kind "icmp" or "mqtt": red when pinged with no replies at all,
    `unmeasured` when never pinged."""
    ms = node["latest"].get(kind + "_ms")
    if ms is not None:
        return latency_color(ms, kind)
    return LOST_COLOR if (kind + "_loss") in node["latest"] else unmeasured


def _icmp_color(node):
    return _probe_color(node, "icmp")


def _draw_ping_blocks(pixels, node, x0, y0, dim, width=3):
    """Ping summary: two blocks (width x 5), ICMP then MQTT, coloured by latency (dark when unmeasured)."""
    for i, kind in enumerate(("icmp", "mqtt")):
        color = _dim(_probe_color(node, kind, unmeasured=SIGNAL_OFF_COLOR), dim)
        start = x0 + i * (width + 1)
        for x in range(start, start + width):
            for y in range(y0, y0 + GLYPH_HEIGHT):
                pixels[x, y] = color


def _fmt_ms(ms, cap=999):
    """Whole ms, capped so it fits: 999 for ICMP (drawn double size), 9999 for MQTT."""
    return "--" if ms is None else "%d" % min(round(ms), cap)


def _overview_nodes(snapshot, metrics):
    """Nodes that report any of `metrics`, live ones first, in stable first-seen order."""
    nodes = [n for n in snapshot["nodes"] if any(m in n["latest"] for m in metrics)]
    nodes.sort(key=lambda n: (n["stale"], n["slot"]))
    return nodes[:MAX_ROWS]


def node_letter(node):
    """First letter of the node's name, for the overview rows ("?" if the font has no glyph)."""
    ch = (node["id"][:1] or "?").upper()
    return ch if ch in _GLYPHS else "?"


def _draw_row_label(pixels, node, y0):
    """Stripe plus the node's initial, both in the node's colour (dimmed when stale)."""
    _draw_stripe(pixels, node, y0)
    draw_text(pixels, LETTER_X, y0 + 1, node_letter(node), _node_color(node))


def _draw_stripe(pixels, node, y0):
    color = _node_color(node)
    for x in range(STRIPE_WIDTH):
        for y in range(y0, y0 + ROW_HEIGHT - 1):
            pixels[x, y] = color


def _draw_corner(pixels, node):
    """Node identity marker in the top-right corner of a detail tile (matches its stripe)."""
    color = _node_color(node)
    for x in range(TILE_SIZE - 2, TILE_SIZE):
        for y in range(2):
            pixels[x, y] = color


def _draw_signal(pixels, x0, y_bottom, rssi, height=7):
    """Four ascending bars, 1px wide with 1px gaps (7px wide); all grey when unknown."""
    level = signal_level(rssi) if rssi is not None else 0
    lit = _SIGNAL_COLORS[level]
    for i in range(4):
        bar_h = max(1, round(height * (i + 1) / 4))
        color = lit if i < level else SIGNAL_OFF_COLOR
        for y in range(y_bottom - bar_h + 1, y_bottom + 1):
            pixels[x0 + i * 2, y] = color


def _draw_trend(pixels, points, color, now, top=TREND_TOP, bottom=TILE_SIZE - 1):
    """Plot `points` [(t, v)] over the last 24h, one column per 45 min (mean per bucket),
    auto-scaled to the data's own min..max."""
    start = now - TREND_SECONDS
    buckets = [[] for _ in range(TILE_SIZE)]
    for t, v in points:
        if t >= start:
            col = min(TILE_SIZE - 1, int((t - start) / TREND_SECONDS * TILE_SIZE))
            buckets[col].append(v)
    means = [sum(b) / len(b) if b else None for b in buckets]
    values = [v for v in means if v is not None]
    if not values:
        return
    lo, hi = min(values), max(values)
    height = bottom - top
    prev_y = None
    for x, v in enumerate(means):
        if v is None:
            prev_y = None
            continue
        y = bottom - round((v - lo) / (hi - lo) * height) if hi > lo else (top + bottom) // 2
        # Join to the previous column so steep changes read as a continuous line.
        y0, y1 = (y, y) if prev_y is None else (min(y, prev_y), max(y, prev_y))
        for yy in range(y0, y1 + 1):
            pixels[x, yy] = color
        prev_y = y


def _new_tile():
    img = Image.new("RGB", (TILE_SIZE, TILE_SIZE), (0, 0, 0))
    return img, img.load()


def generate_env_overview(snapshot):
    """Rows of: stripe + node letter | temperature C (coloured) | humidity % (coloured, right-aligned)."""
    img, pixels = _new_tile()
    for row, node in enumerate(_overview_nodes(snapshot, ("temperature", "humidity"))):
        y0 = row * ROW_HEIGHT
        _draw_row_label(pixels, node, y0)
        dim = STALE_DIM if node["stale"] else 1.0
        temp = node["latest"].get("temperature")
        hum = node["latest"].get("humidity")
        hum_text = _fmt_hum(hum)
        temp_text = _fmt_temp(temp)
        if temp is not None and not _fits(temp_text, hum_text):
            temp_text = "%d" % round(temp)          # e.g. -12.5 -> -13 to leave a gap
        draw_text(pixels, VALUE_X, y0 + 1, temp_text,
                  _dim(temperature_color(temp) if temp is not None else MISSING_COLOR, dim))
        draw_text(pixels, TILE_SIZE - text_width(hum_text), y0 + 1, hum_text,
                  _dim(humidity_color(hum) if hum is not None else MISSING_COLOR, dim))
    return img


def generate_net_overview(snapshot):
    """Rows of: stripe + node letter | Mbps | ping blocks (ICMP, MQTT) | WiFi signal bars."""
    img, pixels = _new_tile()
    for row, node in enumerate(_overview_nodes(snapshot, ("mbps", "rssi"))):
        y0 = row * ROW_HEIGHT
        _draw_row_label(pixels, node, y0)
        dim = STALE_DIM if node["stale"] else 1.0
        mbps = node["latest"].get("mbps")
        draw_text(pixels, VALUE_X, y0 + 1, _fmt_mbps(mbps),
                  _dim(TEXT_COLOR if mbps is not None else MISSING_COLOR, dim))
        _draw_ping_blocks(pixels, node, NET_ROW_BLOCKS_X, y0 + 1, dim, width=2)
        _draw_signal(pixels, TILE_SIZE - 7, y0 + ROW_HEIGHT - 2,
                     None if node["stale"] else node["latest"].get("rssi"))
    return img


def _find_node(snapshot, node_id):
    for node in snapshot["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(node_id)


def generate_env_detail(snapshot, node_id, now=None):
    """Temperature (double size), humidity %, and a 24h temperature trend along the bottom."""
    now = time.time() if now is None else now
    node = _find_node(snapshot, node_id)
    img, pixels = _new_tile()
    dim = STALE_DIM if node["stale"] else 1.0
    temp = node["latest"].get("temperature")
    hum = node["latest"].get("humidity")
    temp_color = temperature_color(temp) if temp is not None else MISSING_COLOR
    draw_text(pixels, 0, 0, _fmt_temp(temp), _dim(temp_color, dim), scale=2)
    hum_color = humidity_color(hum) if hum is not None else MISSING_COLOR
    draw_text(pixels, 0, 13, _fmt_hum(hum) + ("%" if hum is not None else ""), _dim(hum_color, dim))
    _draw_corner(pixels, node)
    _draw_trend(pixels, node["history"]["temperature"], _dim(temp_color, 0.8 * dim), now)
    return img


def generate_net_detail(snapshot, node_id, now=None):
    """Mbps (double size), RSSI dBm, ping blocks and signal bars, and a 24h Mbps trend."""
    now = time.time() if now is None else now
    node = _find_node(snapshot, node_id)
    img, pixels = _new_tile()
    dim = STALE_DIM if node["stale"] else 1.0
    mbps = node["latest"].get("mbps")
    rssi = node["latest"].get("rssi")
    draw_text(pixels, 0, 0, _fmt_mbps(mbps), _dim(TEXT_COLOR if mbps is not None else MISSING_COLOR, dim), scale=2)
    draw_text(pixels, 0, 13, "--" if rssi is None else "%d" % rssi,
              _dim(TEXT_COLOR if rssi is not None else MISSING_COLOR, dim))
    _draw_ping_blocks(pixels, node, PING_BLOCKS_X, 13, dim)
    _draw_signal(pixels, TILE_SIZE - 7, 17, None if node["stale"] else rssi)
    _draw_corner(pixels, node)
    _draw_trend(pixels, node["history"]["mbps"], _dim(TREND_NET_COLOR, dim), now)
    return img


def generate_ping_overview(snapshot):
    """Rows of: stripe + node letter | ICMP ms (left) | MQTT ms (right), each coloured by latency."""
    img, pixels = _new_tile()
    for row, node in enumerate(_overview_nodes(snapshot, PING_METRICS)):
        y0 = row * ROW_HEIGHT
        _draw_row_label(pixels, node, y0)
        dim = STALE_DIM if node["stale"] else 1.0
        icmp = node["latest"].get("icmp_ms")
        mqtt = node["latest"].get("mqtt_ms")
        icmp_text = _fmt_ms(icmp)
        draw_text(pixels, VALUE_X, y0 + 1, icmp_text, _dim(_icmp_color(node), dim))
        mqtt_text = _fmt_ms(mqtt, cap=9999)
        # Only when both are long: MQTT in seconds, "1.4S" then "1S", to keep a gap.
        for shorter in (lambda: "%.1fS" % min(mqtt / 1000, 9.9), lambda: "%dS" % min(round(mqtt / 1000), 9)):
            if mqtt is None or _fits(icmp_text, mqtt_text):
                break
            mqtt_text = shorter()
        draw_text(pixels, TILE_SIZE - text_width(mqtt_text), y0 + 1, mqtt_text,
                  _dim(_probe_color(node, "mqtt"), dim))
    return img


def generate_ping_detail(snapshot, node_id, now=None):
    """ICMP ms (double size), MQTT ms below, and a 24h ICMP trend along the bottom."""
    now = time.time() if now is None else now
    node = _find_node(snapshot, node_id)
    img, pixels = _new_tile()
    dim = STALE_DIM if node["stale"] else 1.0
    icmp = node["latest"].get("icmp_ms")
    mqtt = node["latest"].get("mqtt_ms")
    draw_text(pixels, 0, 0, _fmt_ms(icmp), _dim(_icmp_color(node), dim), scale=2)
    draw_text(pixels, 0, 13, _fmt_ms(mqtt, cap=9999), _dim(_probe_color(node, "mqtt"), dim))
    _draw_corner(pixels, node)
    _draw_trend(pixels, node["history"]["icmp_ms"], _dim(TREND_NET_COLOR, dim), now)
    return img
