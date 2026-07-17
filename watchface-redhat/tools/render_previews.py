#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

WATCHFACE_DIR = Path(__file__).resolve().parents[1]
METRICS_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_metrics.json"
OUT_DIR = WATCHFACE_DIR / "previews"

WIDTH = 200
HEIGHT = 228
OUTER_MARGIN = 2
CENTRAL_GAP_H = 16
BATTERY_BAR_H = 9
BATTERY_BAR_INSET = 5
BATTERY_BAR_RADIUS = 2
BATTERY_BAR_BORDER = 1
BATTERY_VALIDATION_DIR = OUT_DIR / "battery-validation"

STATES = [
    ("08", "36", 75, "08-36"),
    ("10", "11", 70, "10-11"),
    ("11", "11", 50, "11-11"),
    ("12", "34", 66, "12-34"),
    ("20", "58", 30, "20-58"),
    ("01", "05", 15, "01-05"),
    ("06", "49", 8, "06-49"),
    ("09", "06", 10, "09-06"),
    ("18", "18", 85, "18-18"),
    ("22", "22", 40, "22-22"),
]

BATTERY_VALIDATION_LEVELS = [100, 75, 50, 25, 10, 0]


def layout():
    half_h = (HEIGHT - CENTRAL_GAP_H) // 2
    gap_y = half_h
    bar_y = gap_y + (CENTRAL_GAP_H - BATTERY_BAR_H) // 2
    return {
        "hour": (OUTER_MARGIN, 0, WIDTH - OUTER_MARGIN * 2, half_h),
        "minute": (
            OUTER_MARGIN,
            gap_y + CENTRAL_GAP_H,
            WIDTH - OUTER_MARGIN * 2,
            HEIGHT - half_h - CENTRAL_GAP_H,
        ),
        "battery": (
            BATTERY_BAR_INSET,
            bar_y,
            WIDTH - BATTERY_BAR_INSET * 2,
            BATTERY_BAR_H,
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


def draw_battery(canvas, bounds, percent):
    x, y, w, h = bounds
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (x, y, x + w - 1, y + h - 1),
        radius=BATTERY_BAR_RADIUS,
        fill=0,
    )

    border = BATTERY_BAR_BORDER
    inner_x = x + border
    inner_y = y + border
    inner_w = w - border * 2
    inner_h = h - border * 2
    inner_radius = max(0, BATTERY_BAR_RADIUS - border)
    draw.rounded_rectangle(
        (inner_x, inner_y, inner_x + inner_w - 1, inner_y + inner_h - 1),
        radius=inner_radius,
        fill=255,
    )

    percent = max(0, min(100, percent))
    fill_w = (inner_w * percent + 50) // 100
    if fill_w <= 0:
        return

    inner_mask = Image.new("L", (inner_w, inner_h), 0)
    mask_draw = ImageDraw.Draw(inner_mask)
    mask_draw.rounded_rectangle(
        (0, 0, inner_w - 1, inner_h - 1),
        radius=inner_radius,
        fill=255,
    )
    fill_mask = Image.new("L", (inner_w, inner_h), 0)
    fill_draw = ImageDraw.Draw(fill_mask)
    fill_draw.rectangle((0, 0, fill_w - 1, inner_h - 1), fill=255)
    canvas.paste(0, (inner_x, inner_y), ImageChops.multiply(inner_mask, fill_mask))


def render(metrics, hour, minute, battery):
    bounds = layout()
    canvas = Image.new("L", (WIDTH, HEIGHT), 255)

    draw_centered_asset(canvas, load_asset(metrics, hour), bounds["hour"])
    draw_battery(canvas, bounds["battery"], battery)
    draw_centered_asset(canvas, load_asset(metrics, minute), bounds["minute"])
    return canvas


def main():
    metrics = json.loads(METRICS_PATH.read_text())
    OUT_DIR.mkdir(exist_ok=True)
    BATTERY_VALIDATION_DIR.mkdir(exist_ok=True)
    for hour, minute, battery, slug in STATES:
        render(metrics, hour, minute, battery).save(
            OUT_DIR / f"squintless-{slug}-battery-{battery}.png"
        )

    validation_strip = Image.new("L", (WIDTH * len(BATTERY_VALIDATION_LEVELS), HEIGHT), 255)
    for index, battery in enumerate(BATTERY_VALIDATION_LEVELS):
        preview = render(metrics, "08", "36", battery)
        preview.save(BATTERY_VALIDATION_DIR / f"squintless-08-36-battery-{battery:03d}.png")
        validation_strip.paste(preview, (WIDTH * index, 0))
    validation_strip.save(BATTERY_VALIDATION_DIR / "squintless-battery-validation-strip.png")


if __name__ == "__main__":
    main()
