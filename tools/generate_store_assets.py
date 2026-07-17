#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WATCHFACE_DIR = ROOT / "watchface"
METRICS_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_metrics.json"

STORE_DIR = ROOT / "store"
ICON_DIR = STORE_DIR / "icon"
FEATURE_DIR = STORE_DIR / "feature"
SCREENSHOT_DIR = STORE_DIR / "screenshots"
WATCHFACE_RESOURCE_DIR = WATCHFACE_DIR / "resources" / "images"

WIDTH = 200
HEIGHT = 228
OUTER_MARGIN = 2
CENTRAL_GAP_H = 16
BATTERY_LINE_H = 7
BATTERY_LINE_INSET = 5
LOW_BATTERY_MIN_W = 8
BATTERY_REMAINDER_GRAY = 218

TAGLINE = "Designed for your aging eyes, not your ego."

FONT_BLACK = Path("/System/Library/Fonts/Supplemental/Arial Black.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
FONT_REGULAR = Path("/System/Library/Fonts/Supplemental/Arial.ttf")


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def ensure_dirs() -> None:
    for directory in [ICON_DIR, FEATURE_DIR, SCREENSHOT_DIR, WATCHFACE_RESOURCE_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


def layout() -> dict[str, tuple[int, int, int, int]]:
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


def load_metrics() -> dict:
    return json.loads(METRICS_PATH.read_text())


def load_face_asset(metrics: dict, text: str) -> Image.Image:
    if len(text) == 1:
        path = WATCHFACE_DIR / metrics["singles"][text]["file"]
    else:
        path = WATCHFACE_DIR / metrics["pairs"][text]["file"]
    return Image.open(path).convert("L")


def draw_centered_asset(canvas: Image.Image, asset: Image.Image, bounds: tuple[int, int, int, int]) -> None:
    x, y, w, h = bounds
    canvas.paste(asset, (x + (w - asset.width) // 2, y + (h - asset.height) // 2))


def render_face(metrics: dict, hour: str, minute: str, battery: int) -> Image.Image:
    bounds = layout()
    canvas = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(canvas)
    draw_centered_asset(canvas, load_face_asset(metrics, hour), bounds["hour"])
    draw_battery(draw, bounds["battery"], battery)
    draw_centered_asset(canvas, load_face_asset(metrics, minute), bounds["minute"])
    return canvas


def draw_battery(draw: ImageDraw.ImageDraw, bounds: tuple[int, int, int, int], percent: int) -> None:
    x, y, w, h = bounds
    fill_w = w * percent // 100
    if percent > 0 and fill_w < LOW_BATTERY_MIN_W:
        fill_w = LOW_BATTERY_MIN_W
    draw.rectangle((x, y, x + w - 1, y + h - 1), fill=BATTERY_REMAINDER_GRAY)
    if fill_w > 0:
        draw.rectangle((x, y, x + fill_w - 1, y + h - 1), fill=0)


def gradient(size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    w, h = size
    out = Image.new("RGB", size)
    draw = ImageDraw.Draw(out)
    for y in range(h):
        t = y / max(1, h - 1)
        color = tuple(round(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        draw.line((0, y, w, y), fill=color)
    return out


def add_shadow(base: Image.Image, box: tuple[int, int, int, int], blur: int, opacity: int) -> None:
    shadow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    draw.ellipse(box, fill=(0, 0, 0, opacity))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(shadow)


def paste_center(base: Image.Image, item: Image.Image, center: tuple[int, int]) -> tuple[int, int]:
    x = int(center[0] - item.width / 2)
    y = int(center[1] - item.height / 2)
    base.alpha_composite(item, (x, y))
    return x, y


def make_watch(face: Image.Image, scale: float = 2.0) -> Image.Image:
    s = scale
    screen_w = round(WIDTH * s)
    screen_h = round(HEIGHT * s)
    bezel = round(26 * s)
    case_pad_x = round(48 * s)
    case_pad_y = round(42 * s)
    strap_w = round(110 * s)
    strap_h = round(108 * s)
    case_w = screen_w + case_pad_x * 2
    case_h = screen_h + case_pad_y * 2
    canvas_w = case_w + round(80 * s)
    canvas_h = case_h + strap_h * 2 + round(60 * s)
    out = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(out)

    cx = canvas_w // 2
    case_x = (canvas_w - case_w) // 2
    case_y = strap_h + round(28 * s)
    radius = round(46 * s)

    strap_x = cx - strap_w // 2
    draw.rounded_rectangle(
        (strap_x, 0, strap_x + strap_w, case_y + round(30 * s)),
        radius=round(20 * s),
        fill=(18, 18, 18, 255),
    )
    draw.rounded_rectangle(
        (strap_x, case_y + case_h - round(30 * s), strap_x + strap_w, canvas_h),
        radius=round(20 * s),
        fill=(18, 18, 18, 255),
    )
    for offset, alpha in [(0, 255), (6, 80), (12, 50)]:
        draw.rounded_rectangle(
            (
                case_x + offset,
                case_y + offset,
                case_x + case_w - offset,
                case_y + case_h - offset,
            ),
            radius=max(8, radius - offset),
            outline=(245, 245, 240, alpha),
            width=max(1, round(2 * s)),
        )
    draw.rounded_rectangle(
        (case_x, case_y, case_x + case_w, case_y + case_h),
        radius=radius,
        fill=(172, 170, 164, 255),
        outline=(245, 245, 238, 255),
        width=round(3 * s),
    )
    draw.rounded_rectangle(
        (
            case_x + round(8 * s),
            case_y + round(8 * s),
            case_x + case_w - round(8 * s),
            case_y + case_h - round(8 * s),
        ),
        radius=round(38 * s),
        outline=(103, 103, 99, 150),
        width=max(1, round(2 * s)),
    )
    bezel_x = case_x + case_pad_x - bezel
    bezel_y = case_y + case_pad_y - bezel
    bezel_w = screen_w + bezel * 2
    bezel_h = screen_h + bezel * 2
    draw.rounded_rectangle(
        (bezel_x, bezel_y, bezel_x + bezel_w, bezel_y + bezel_h),
        radius=round(34 * s),
        fill=(4, 4, 4, 255),
    )

    screen_x = case_x + case_pad_x
    screen_y = case_y + case_pad_y
    draw.rounded_rectangle(
        (screen_x, screen_y, screen_x + screen_w, screen_y + screen_h),
        radius=round(13 * s),
        fill=(255, 255, 255, 255),
    )
    scaled_face = face.convert("RGB").resize((screen_w, screen_h), Image.Resampling.NEAREST).convert("RGBA")
    screen_mask = Image.new("L", (screen_w, screen_h), 0)
    mask_draw = ImageDraw.Draw(screen_mask)
    mask_draw.rounded_rectangle((0, 0, screen_w, screen_h), radius=round(12 * s), fill=255)
    clipped = Image.new("RGBA", (screen_w, screen_h), (255, 255, 255, 0))
    clipped.alpha_composite(scaled_face)
    out.paste(clipped, (screen_x, screen_y), screen_mask)

    highlight = Image.new("RGBA", out.size, (0, 0, 0, 0))
    hdraw = ImageDraw.Draw(highlight)
    hdraw.line(
        (case_x + round(42 * s), case_y + round(16 * s), case_x + case_w - round(60 * s), case_y + round(8 * s)),
        fill=(255, 255, 255, 70),
        width=max(1, round(2 * s)),
    )
    out.alpha_composite(highlight)
    return out


def make_app_icon(face: Image.Image, size: int) -> Image.Image:
    high = size * 4
    icon = Image.new("L", (high, high), 0)
    draw = ImageDraw.Draw(icon)
    margin = round(high * 0.105)
    radius = round(high * 0.115)
    draw.rounded_rectangle((margin, margin, high - margin, high - margin), radius=radius, fill=255)
    face_w = round(high * 0.70)
    face_h = round(face_w * HEIGHT / WIDTH)
    scaled = face.resize((face_w, face_h), Image.Resampling.NEAREST)
    icon.paste(scaled, ((high - face_w) // 2, (high - face_h) // 2))
    icon = icon.resize((size, size), Image.Resampling.LANCZOS)
    return icon.point(lambda value: 0 if value < 128 else 255, mode="1").convert("L")


def write_icons(face: Image.Image) -> None:
    for size in [512, 144, 72, 48]:
        make_app_icon(face, size).save(ICON_DIR / f"squintless-icon-{size}.png")
    make_app_icon(face, 25).save(WATCHFACE_RESOURCE_DIR / "menu_icon.png")


def screenshot_front(face: Image.Image, out_path: Path, scale: float, center_y: int, background: tuple[tuple[int, int, int], tuple[int, int, int]]) -> None:
    base = gradient((1000, 1400), background[0], background[1]).convert("RGBA")
    add_shadow(base, (250, 1035, 750, 1240), 52, 80)
    watch = make_watch(face, scale)
    paste_center(base, watch, (500, center_y))
    base.convert("RGB").save(out_path, quality=95)


def screenshot_wrist(face: Image.Image, out_path: Path) -> None:
    base = gradient((1000, 1400), (232, 232, 228), (202, 202, 196)).convert("RGBA")
    arm = Image.new("RGBA", (1300, 430), (0, 0, 0, 0))
    adraw = ImageDraw.Draw(arm)
    adraw.rounded_rectangle((0, 70, 1300, 355), radius=130, fill=(181, 128, 96, 255))
    adraw.rounded_rectangle((60, 90, 1280, 210), radius=85, fill=(205, 151, 112, 75))
    arm = arm.rotate(-18, expand=True, resample=Image.Resampling.BICUBIC)
    base.alpha_composite(arm, (-210, 610))
    add_shadow(base, (205, 760, 825, 1095), 58, 90)
    watch = make_watch(face, 1.85).rotate(-13, expand=True, resample=Image.Resampling.BICUBIC)
    paste_center(base, watch, (520, 775))
    base.convert("RGB").save(out_path, quality=95)


def screenshot_closeup(face: Image.Image, out_path: Path) -> None:
    base = gradient((1000, 1400), (250, 250, 247), (224, 224, 219)).convert("RGBA")
    scaled = face.resize((920, 1049), Image.Resampling.NEAREST).convert("RGBA")
    draw = ImageDraw.Draw(base)
    draw.rectangle((0, 96, 1000, 1304), fill=(5, 5, 5, 255))
    draw.rounded_rectangle((40, 146, 960, 1195), radius=28, fill=(255, 255, 255, 255))
    base.alpha_composite(scaled, (40, 146))
    base.convert("RGB").save(out_path, quality=95)


def write_screenshots(metrics: dict) -> None:
    screenshot_front(
        render_face(metrics, "08", "36", 75),
        SCREENSHOT_DIR / "01-straight-on-hero.png",
        1.82,
        700,
        ((246, 246, 243), (214, 214, 208)),
    )
    screenshot_wrist(render_face(metrics, "11", "11", 50), SCREENSHOT_DIR / "02-angled-wrist-readability.png")
    screenshot_closeup(render_face(metrics, "12", "34", 66), SCREENSHOT_DIR / "03-large-time-close-up.png")
    screenshot_front(
        render_face(metrics, "20", "58", 2),
        SCREENSHOT_DIR / "04-battery-almost-empty.png",
        1.70,
        705,
        ((244, 244, 240), (211, 211, 204)),
    )
    screenshot_front(
        render_face(metrics, "22", "22", 40),
        SCREENSHOT_DIR / "05-pair-spacing.png",
        1.74,
        700,
        ((248, 248, 245), (219, 219, 214)),
    )


def write_feature(metrics: dict) -> None:
    base = gradient((1600, 900), (248, 248, 245), (218, 218, 212)).convert("RGBA")
    draw = ImageDraw.Draw(base)
    title = font(FONT_BLACK, 132)
    tagline_font = font(FONT_REGULAR, 36)
    small = font(FONT_REGULAR, 30)
    draw.text((120, 230), "Squintless", fill=(0, 0, 0), font=title)
    draw.text((124, 388), TAGLINE, fill=(24, 24, 24), font=tagline_font)
    draw.text((126, 470), "A Pebble Time 2 watch face for instant readability.", fill=(70, 70, 70), font=small)
    add_shadow(base, (1015, 690, 1515, 835), 60, 85)
    watch = make_watch(render_face(metrics, "08", "36", 75), 1.42)
    paste_center(base, watch, (1260, 450))
    base.convert("RGB").save(FEATURE_DIR / "squintless-feature-1600x900.png", quality=95)


def main() -> None:
    ensure_dirs()
    metrics = load_metrics()
    face = render_face(metrics, "08", "36", 75)
    write_icons(face)
    write_feature(metrics)
    write_screenshots(metrics)


if __name__ == "__main__":
    main()
