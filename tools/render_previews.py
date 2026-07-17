#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw

WIDTH = 200
HEIGHT = 228
DIGIT_UNITS_W = 13
DIGIT_UNITS_H = 15
SOLID_ONE_UNITS_W = 11

OUTER_MARGIN = 2
CENTRAL_GAP_H = 16
BATTERY_LINE_H = 7
BATTERY_LINE_INSET = 5
DEFAULT_DIGIT_SPACING_UNITS = 1
DIGIT_CORNER_RADIUS = 2
LOW_BATTERY_MIN_W = 8

SEGMENTED = "segmented"
SOLID = "solid"

STATES = [
    ("08", "36", 75, "08-36"),
    ("11", "11", 50, "11-11"),
    ("12", "34", 66, "12-34"),
    ("20", "58", 30, "20-58"),
    ("1", "05", 15, "1-05-12h"),
    ("6", "49", 8, "6-49-12h"),
    ("9", "06", 10, "9-06-12h"),
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


def rect(draw, origin, scale, radius, x, y, w, h, fill=0):
    x0 = origin[0] + x * scale
    y0 = origin[1] + y * scale
    x1 = x0 + w * scale - 1
    y1 = y0 + h * scale - 1
    draw.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill)


def top(draw, origin, scale, radius):
    rect(draw, origin, scale, radius, 3, 0, 7, 3)


def upper_left(draw, origin, scale, radius):
    rect(draw, origin, scale, radius, 0, 2, 3, 6)


def upper_right(draw, origin, scale, radius):
    rect(draw, origin, scale, radius, 10, 2, 3, 6)


def middle(draw, origin, scale, radius):
    rect(draw, origin, scale, radius, 3, 6, 7, 3)


def lower_left(draw, origin, scale, radius):
    rect(draw, origin, scale, radius, 0, 7, 3, 6)


def lower_right(draw, origin, scale, radius):
    rect(draw, origin, scale, radius, 10, 7, 3, 6)


def bottom(draw, origin, scale, radius):
    rect(draw, origin, scale, radius, 3, 12, 7, 3)


def draw_segmented_digit(draw, digit, origin, scale, radius):
    segments = {
        "0": [top, upper_left, upper_right, lower_left, lower_right, bottom],
        "2": [top, upper_right, middle, lower_left, bottom],
        "3": [top, upper_right, middle, lower_right, bottom],
        "4": [upper_left, upper_right, middle, lower_right],
        "5": [top, upper_left, middle, lower_right, bottom],
        "6": [top, upper_left, middle, lower_left, lower_right, bottom],
        "8": [top, upper_left, upper_right, middle, lower_left, lower_right, bottom],
        "9": [top, upper_left, upper_right, middle, lower_right, bottom],
    }
    if digit == "1":
        rect(draw, origin, scale, radius, 3, 2, 4, 3)
        rect(draw, origin, scale, radius, 6, 0, 4, 13)
        rect(draw, origin, scale, radius, 2, 12, 9, 3)
    elif digit == "7":
        top(draw, origin, scale, radius)
        upper_right(draw, origin, scale, radius)
        lower_right(draw, origin, scale, radius)
        rect(draw, origin, scale, radius, 7, 5, 3, 4)
    else:
        for segment in segments[digit]:
            segment(draw, origin, scale, radius)


def draw_solid_digit(draw, digit, origin, scale, radius):
    inner_radius = radius // 2
    if digit == "0":
        rect(draw, origin, scale, radius, 0, 0, 13, 15)
        rect(draw, origin, scale, inner_radius, 4, 3, 5, 9, fill=1)
    elif digit == "1":
        rect(draw, origin, scale, radius, 1, 0, 8, 4)
        rect(draw, origin, scale, radius, 4, 0, 5, 15)
        rect(draw, origin, scale, radius, 0, 11, 11, 4)
    elif digit == "2":
        rect(draw, origin, scale, radius, 0, 0, 13, 15)
        rect(draw, origin, scale, inner_radius, 0, 4, 7, 3, fill=1)
        rect(draw, origin, scale, inner_radius, 6, 9, 7, 3, fill=1)
    elif digit == "3":
        rect(draw, origin, scale, radius, 0, 0, 13, 15)
        rect(draw, origin, scale, inner_radius, 0, 3, 8, 3, fill=1)
        rect(draw, origin, scale, inner_radius, 0, 9, 8, 3, fill=1)
    elif digit == "4":
        rect(draw, origin, scale, radius, 0, 0, 4, 9)
        rect(draw, origin, scale, radius, 8, 0, 5, 15)
        rect(draw, origin, scale, radius, 0, 6, 13, 4)
    elif digit == "5":
        rect(draw, origin, scale, radius, 0, 0, 13, 15)
        rect(draw, origin, scale, inner_radius, 6, 4, 7, 3, fill=1)
        rect(draw, origin, scale, inner_radius, 0, 9, 7, 3, fill=1)
    elif digit == "6":
        rect(draw, origin, scale, radius, 0, 0, 13, 15)
        rect(draw, origin, scale, inner_radius, 5, 3, 8, 3, fill=1)
        rect(draw, origin, scale, inner_radius, 4, 9, 5, 3, fill=1)
    elif digit == "7":
        rect(draw, origin, scale, radius, 0, 0, 13, 4)
        rect(draw, origin, scale, radius, 8, 3, 5, 4)
        rect(draw, origin, scale, radius, 6, 6, 5, 4)
        rect(draw, origin, scale, radius, 4, 9, 5, 6)
    elif digit == "8":
        rect(draw, origin, scale, radius, 0, 0, 13, 15)
        rect(draw, origin, scale, inner_radius, 4, 3, 5, 3, fill=1)
        rect(draw, origin, scale, inner_radius, 4, 9, 5, 3, fill=1)
    elif digit == "9":
        rect(draw, origin, scale, radius, 0, 0, 13, 15)
        rect(draw, origin, scale, inner_radius, 4, 3, 5, 3, fill=1)
        rect(draw, origin, scale, inner_radius, 0, 9, 8, 3, fill=1)


def digit_width_units(digit, style):
    if style == SOLID and digit == "1":
        return SOLID_ONE_UNITS_W
    return DIGIT_UNITS_W


def spacing_units(left, right, style):
    if style == SOLID:
        if left == "1" and right == "1":
            return 3
        if left == "1" or right == "1":
            return 2
        if (left, right) in {("0", "8"), ("8", "8")}:
            return 1
    return DEFAULT_DIGIT_SPACING_UNITS


def number_width_units(text, style):
    total = 0
    for index, digit in enumerate(text):
        total += digit_width_units(digit, style)
        if index < len(text) - 1:
            total += spacing_units(digit, text[index + 1], style)
    return total


def draw_number(draw, text, bounds, style):
    x, y, w, h = bounds
    total_units_w = number_width_units(text, style)
    scale = min(w // total_units_w, h // DIGIT_UNITS_H)
    number_w = total_units_w * scale
    number_h = DIGIT_UNITS_H * scale
    radius = DIGIT_CORNER_RADIUS * scale
    digit_x = x + (w - number_w) // 2
    origin_y = y + (h - number_h) // 2

    for index, digit in enumerate(text):
        if style == SOLID:
            draw_solid_digit(draw, digit, (digit_x, origin_y), scale, radius)
        else:
            draw_segmented_digit(draw, digit, (digit_x, origin_y), scale, radius)
        digit_x += digit_width_units(digit, style) * scale
        if index < len(text) - 1:
            digit_x += spacing_units(digit, text[index + 1], style) * scale


def render(hour, minute, battery, style):
    bounds = layout()
    image = Image.new("1", (WIDTH, HEIGHT), 1)
    draw = ImageDraw.Draw(image)

    draw_number(draw, hour, bounds["hour"], style)

    x, y, w, h = bounds["battery"]
    fill_w = w * battery // 100
    if battery > 0 and fill_w < LOW_BATTERY_MIN_W:
        fill_w = LOW_BATTERY_MIN_W
    draw.rectangle((x, y, x + fill_w - 1, y + h - 1), fill=0)

    draw_number(draw, minute, bounds["minute"], style)
    return image


def save_comparison(segmented, solid, path):
    gap = 8
    image = Image.new("1", (WIDTH * 2 + gap, HEIGHT), 1)
    image.paste(segmented, (0, 0))
    image.paste(solid, (WIDTH + gap, 0))
    path.parent.mkdir(exist_ok=True)
    image.save(path)


def main():
    out_dir = Path("screenshots")
    out_dir.mkdir(exist_ok=True)
    for hour, minute, battery, slug in STATES:
        segmented = render(hour, minute, battery, SEGMENTED)
        solid = render(hour, minute, battery, SOLID)
        segmented.save(out_dir / f"segmented-{slug}-battery-{battery}.png")
        solid.save(out_dir / f"solid-{slug}-battery-{battery}.png")
        save_comparison(segmented, solid, out_dir / f"compare-{slug}-battery-{battery}.png")


if __name__ == "__main__":
    main()
