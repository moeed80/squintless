#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

WATCHFACE_DIR = Path(__file__).resolve().parents[1]
METRICS_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_metrics.json"
DATE_METRICS_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_date_metrics.json"
OUT_DIR = WATCHFACE_DIR / "previews"

PROFILES = {
    "emery_200x228": {
        "output_dir": OUT_DIR,
        "width": 200,
        "height": 228,
        "outer_margin": 2,
        "central_gap_h": 16,
        "battery_bar_h": 9,
        "battery_bar_inset": 5,
        "battery_bar_radius": 2,
        "battery_bar_border": 1,
    },
    "rect_144x168": {
        "output_dir": OUT_DIR / "rect-144x168",
        "width": 144,
        "height": 168,
        "outer_margin": 2,
        "central_gap_h": 14,
        "battery_bar_h": 7,
        "battery_bar_inset": 4,
        "battery_bar_radius": 2,
        "battery_bar_border": 1,
    },
    "aplite_144x168": {
        "asset_profile_key": "rect_144x168",
        "output_dir": OUT_DIR / "aplite-144x168",
        "width": 144,
        "height": 168,
        "outer_margin": 2,
        "central_gap_h": 14,
        "battery_bar_h": 7,
        "battery_bar_inset": 4,
        "battery_bar_radius": 2,
        "battery_bar_border": 1,
        "use_single_composition": True,
    },
}

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

DATE_GLANCE_STATES = [
    ("JUL", "22", "jul-22"),
    ("DEC", "31", "dec-31"),
]


def layout(profile):
    half_h = (profile["height"] - profile["central_gap_h"]) // 2
    gap_y = half_h
    bar_y = gap_y + (profile["central_gap_h"] - profile["battery_bar_h"]) // 2
    return {
        "hour": (
            profile["outer_margin"],
            0,
            profile["width"] - profile["outer_margin"] * 2,
            half_h,
        ),
        "minute": (
            profile["outer_margin"],
            gap_y + profile["central_gap_h"],
            profile["width"] - profile["outer_margin"] * 2,
            profile["height"] - half_h - profile["central_gap_h"],
        ),
        "battery": (
            profile["battery_bar_inset"],
            bar_y,
            profile["width"] - profile["battery_bar_inset"] * 2,
            profile["battery_bar_h"],
        ),
    }


def profile_metrics(metrics, profile_key):
    return metrics.get("profiles", {}).get(profile_key, metrics)


def load_asset(metrics, profile_key, text):
    metrics = profile_metrics(metrics, profile_key)
    if len(text) == 1:
        path = WATCHFACE_DIR / metrics["singles"][text]["file"]
    else:
        path = WATCHFACE_DIR / metrics["pairs"][text]["file"]
    return Image.open(path).convert("L")


def load_date_month_asset(metrics, profile_key, month):
    metrics = profile_metrics(metrics, profile_key)
    return Image.open(WATCHFACE_DIR / metrics["months"][month]["file"]).convert("L")


def load_date_day_asset(metrics, profile_key, day):
    metrics = profile_metrics(metrics, profile_key)
    return Image.open(WATCHFACE_DIR / metrics["days"][day]["file"]).convert("L")


def draw_centered_asset(canvas, asset, bounds):
    x, y, w, h = bounds
    ax = x + (w - asset.width) // 2
    ay = y + (h - asset.height) // 2
    canvas.paste(asset, (ax, ay))


def pair_spacing(metrics, text):
    return metrics["pair_spacing"].get(text, metrics["default_pair_spacing"])


def draw_time_asset(canvas, metrics, profile_key, profile, text, bounds):
    if not profile.get("use_single_composition") or len(text) == 1:
        draw_centered_asset(canvas, load_asset(metrics, profile_key, text), bounds)
        return

    left = load_asset(metrics, profile_key, text[0])
    right = load_asset(metrics, profile_key, text[1])
    spacing = max(0, pair_spacing(metrics, text))
    row_h = max(left.height, right.height)
    total_w = left.width + spacing + right.width
    x, y, w, h = bounds
    ax = x + (w - total_w) // 2
    ay = y + (h - row_h) // 2

    canvas.paste(left, (ax, ay + (row_h - left.height) // 2))
    canvas.paste(right, (ax + left.width + spacing, ay + (row_h - right.height) // 2))


def draw_battery(canvas, profile, bounds, percent):
    x, y, w, h = bounds
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(
        (x, y, x + w - 1, y + h - 1),
        radius=profile["battery_bar_radius"],
        fill=0,
    )

    border = profile["battery_bar_border"]
    inner_x = x + border
    inner_y = y + border
    inner_w = w - border * 2
    inner_h = h - border * 2
    inner_radius = max(0, profile["battery_bar_radius"] - border)
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


def draw_date_separator(canvas, profile, bounds):
    x, y, w, h = bounds
    center_x = x + w // 2
    stroke_w = 2 if profile["battery_bar_h"] <= 7 else 3
    x_offset = 4 if profile["battery_bar_h"] <= 7 else 5
    draw = ImageDraw.Draw(canvas)
    draw.line(
        (center_x + x_offset, y - 1, center_x - x_offset, y + h),
        fill=0,
        width=stroke_w,
    )


def render(metrics, profile_key, profile, hour, minute, battery):
    bounds = layout(profile)
    canvas = Image.new("L", (profile["width"], profile["height"]), 255)

    draw_time_asset(canvas, metrics, profile_key, profile, hour, bounds["hour"])
    draw_battery(canvas, profile, bounds["battery"], battery)
    draw_time_asset(canvas, metrics, profile_key, profile, minute, bounds["minute"])
    return canvas


def render_date_glance(date_metrics, profile_key, profile, month, day):
    bounds = layout(profile)
    canvas = Image.new("L", (profile["width"], profile["height"]), 255)

    draw_centered_asset(
        canvas,
        load_date_month_asset(date_metrics, profile_key, month),
        bounds["hour"],
    )
    draw_date_separator(canvas, profile, bounds["battery"])
    draw_centered_asset(
        canvas,
        load_date_day_asset(date_metrics, profile_key, day),
        bounds["minute"],
    )
    return canvas


def main():
    metrics = json.loads(METRICS_PATH.read_text())
    date_metrics = json.loads(DATE_METRICS_PATH.read_text())

    for profile_key, profile in PROFILES.items():
        asset_profile_key = profile.get("asset_profile_key", profile_key)
        output_dir = profile["output_dir"]
        battery_validation_dir = output_dir / "battery-validation"
        date_glance_dir = output_dir / "date-glance"
        output_dir.mkdir(parents=True, exist_ok=True)
        battery_validation_dir.mkdir(parents=True, exist_ok=True)
        date_glance_dir.mkdir(parents=True, exist_ok=True)

        for hour, minute, battery, slug in STATES:
            render(metrics, asset_profile_key, profile, hour, minute, battery).save(
                output_dir / f"squintless-{slug}-battery-{battery}.png"
            )

        for month, day, slug in DATE_GLANCE_STATES:
            render_date_glance(date_metrics, asset_profile_key, profile, month, day).save(
                date_glance_dir / f"squintless-date-{slug}.png"
            )

        validation_strip = Image.new(
            "L",
            (profile["width"] * len(BATTERY_VALIDATION_LEVELS), profile["height"]),
            255,
        )
        for index, battery in enumerate(BATTERY_VALIDATION_LEVELS):
            preview = render(metrics, asset_profile_key, profile, "08", "36", battery)
            preview.save(
                battery_validation_dir / f"squintless-08-36-battery-{battery:03d}.png"
            )
            validation_strip.paste(preview, (profile["width"] * index, 0))
        validation_strip.save(battery_validation_dir / "squintless-battery-validation-strip.png")


if __name__ == "__main__":
    main()
