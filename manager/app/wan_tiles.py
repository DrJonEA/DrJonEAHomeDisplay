"""32x32 tile for the external network view (see unifi.fetch_wan).

  rows 0-4    ↓ ISP download Mbps (last speed test)          internet latency ms
  rows 6-10   ↑ ISP upload Mbps
  rows 12-16  cloud latency: two cells of <letter><ms>, e.g. G14  M15
  rows 18-22  two more cells (C = Cloudflare, A = Amazon, U = Ubiquiti, ...)
  rows 24-31  24h WAN traffic: download (cyan) and upload (orange) on one Mbps scale

Colours: download/upload text matches its trend line; latencies use the "internet" bands
(green < 30 ms, yellow < 80 ms, red above or no reply).
"""
import time

from .images import TILE_SIZE
from .sensor_tiles import (
    MISSING_COLOR,
    _new_tile,
    draw_text,
    latency_color,
    text_width,
)

DOWN_COLOR = (0, 200, 255)
UP_COLOR = (255, 150, 0)
LABEL_COLOR = (150, 150, 150)
LOST_COLOR = (255, 40, 40)
TREND_TOP = 24
TREND_SECONDS = 24 * 60 * 60
MAX_MONITORS = 4


def _fmt_mbps(m):
    if m is None:
        return "--"
    return "%d" % round(min(m, 9999)) if m >= 100 else "%.1f" % m


def _fmt_ms(ms):
    return "--" if ms is None else "%d" % min(round(ms), 999)


def _bucket_means(points, now, key):
    start = now - TREND_SECONDS
    buckets = [[] for _ in range(TILE_SIZE)]
    for p in points:
        if p["time"] >= start:
            col = min(TILE_SIZE - 1, int((p["time"] - start) / TREND_SECONDS * TILE_SIZE))
            buckets[col].append(p[key])
    return [sum(b) / len(b) if b else None for b in buckets]


def _draw_series(pixels, means, hi, color, top=TREND_TOP, bottom=TILE_SIZE - 1):
    height = bottom - top
    prev = None
    for x, v in enumerate(means):
        if v is None:
            prev = None
            continue
        y = bottom - round(v / hi * height) if hi > 0 else bottom
        y0, y1 = (y, y) if prev is None else (min(y, prev), max(y, prev))
        for yy in range(y0, y1 + 1):
            pixels[x, yy] = color
        prev = y


def generate_wan_tile(wan, now=None):
    now = time.time() if now is None else now
    img, pixels = _new_tile()
    last = wan.get("last_speedtest") or {}

    down, up = last.get("down_mbps"), last.get("up_mbps")
    draw_text(pixels, 0, 0, "↓" + _fmt_mbps(down), DOWN_COLOR if down is not None else MISSING_COLOR)
    draw_text(pixels, 0, 6, "↑" + _fmt_mbps(up), UP_COLOR if up is not None else MISSING_COLOR)

    latency = wan.get("latency_ms")
    lat_text = _fmt_ms(latency)
    draw_text(pixels, TILE_SIZE - text_width(lat_text), 0, lat_text,
              latency_color(latency, "internet") if latency is not None else MISSING_COLOR)

    for i, m in enumerate(wan.get("monitors", [])[:MAX_MONITORS]):
        x = 0 if i % 2 == 0 else 17
        y = 12 + (i // 2) * 6
        draw_text(pixels, x, y, m.get("label", "?"), LABEL_COLOR)
        ms = m.get("latency_ms")
        draw_text(pixels, x + 4, y, _fmt_ms(ms), latency_color(ms, "internet") if ms is not None else LOST_COLOR)

    points = wan.get("throughput_5min", [])
    down_means = _bucket_means(points, now, "down_mbps")
    up_means = _bucket_means(points, now, "up_mbps")
    values = [v for v in down_means + up_means if v is not None]
    if values:
        hi = max(values)
        _draw_series(pixels, up_means, hi, UP_COLOR)
        _draw_series(pixels, down_means, hi, DOWN_COLOR)  # download on top where they cross
    return img
