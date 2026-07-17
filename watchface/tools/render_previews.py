#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

WATCHFACE_DIR = Path(__file__).resolve().parents[1]
METRICS_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_metrics.json"
OUT_DIR = WATCHFACE_DIR / "previews"

WIDTH = 200
HEIGHT = 228
OUTER_MARGIN = 2
CENTRAL_GAP_H = 16
BATTERY_LINE_H = 7
BATTERY_LINE_INSET = 5
LOW_BATTERY_MIN_W = 8
BATTERY_REMAINDER_GRAY = 218

STATES = [
    ("08", "36", 75, "08-36"),
    ("11", "11", 50, "11-11"),
    ("12", "34", 66, "12-34"),
    ("20", "58", 30, "20-58"),
    ("01", "05", 15, "01-05"),
    ("06", "49", 8, "06-49"),
    ("09", "06", 10, "09-06"),
    ("18", "18", 85, "18-18"),
    ("22", "22", 40, "22-22"),
]


def layout():
    half_h = (HEIGHT - CENTRAL_GAP_H) // 2
    gap_y = half_h
    line_y = gap_y + (CENTRAL_GAP_H - BATTERY_LINE_H) // 2
    return {
        "hour": (OUTER_MARGIN, 0, WIDTH - OUTER_MARGIN * 2, half_h),
        "minute": (
            OUTER_MARGIN,
            gap_y + CENTRAL_GAP_H,
            WIDTH - OUTER_MARGIN * 2,
            HEIGHT - half_h - CENTRAL_GAP_H,
        ),
        "battery": (
            BATTERY_LINE_INSET,
            line_y,
            WIDTH - BATTERY_LINE_INSET * 2,
            BATTERY_LINE_H,
        ),
    }


def load_asset(metrics, text):
    if len(text) == 1:
        path = WATCHFACE_DIR / metrics["singles"][text]["file"]
    else:
        path = WATCHFACE_DIR / metrics["pairs"][text]["file"]
    return Image.open(path).convert("L")


def draw_centered_asset(canvas, asset, bounds):
    x, y, w, h = bounds
    ax = x + (w - asset.width) // 2
    ay = y + (h - asset.height) // 2
    canvas.paste(asset, (ax, ay))


def draw_battery(draw, bounds, percent):
    x, y, w, h = bounds
    fill_w = w * percent // 100
    if percent > 0 and fill_w < LOW_BATTERY_MIN_W:
        fill_w = LOW_BATTERY_MIN_W
    draw.rectangle((x, y, x + w - 1, y + h - 1), fill=BATTERY_REMAINDER_GRAY)
    if fill_w > 0:
        draw.rectangle((x, y, x + fill_w - 1, y + h - 1), fill=0)


def render(metrics, hour, minute, battery):
    bounds = layout()
    canvas = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(canvas)

    draw_centered_asset(canvas, load_asset(metrics, hour), bounds["hour"])
    draw_battery(draw, bounds["battery"], battery)
    draw_centered_asset(canvas, load_asset(metrics, minute), bounds["minute"])
    return canvas


def main():
    metrics = json.loads(METRICS_PATH.read_text())
    OUT_DIR.mkdir(exist_ok=True)
    for hour, minute, battery, slug in STATES:
        render(metrics, hour, minute, battery).save(
            OUT_DIR / f"squintless-{slug}-battery-{battery}.png"
        )


if __name__ == "__main__":
    main()
