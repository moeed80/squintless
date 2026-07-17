#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_PATH = ROOT / "typeface" / "font-edition" / "fonts" / "RedHatDisplay-wght.ttf"
WATCHFACE_DIR = ROOT / "watchface-font"
RESOURCE_DIR = WATCHFACE_DIR / "resources" / "images"
SINGLE_DIR = RESOURCE_DIR / "singles"
PAIR_DIR = RESOURCE_DIR / "pairs"
HEADER_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_assets.h"
METRICS_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_metrics.json"
PACKAGE_PATH = WATCHFACE_DIR / "package.json"

RESOURCE_GLYPH_HEIGHT = 100
ROW_WIDTH = 196
FONT_WEIGHT = 900

PAIR_SPACING = {
    "00": 2,
    "08": 1,
    "10": 5,
    "11": 12,
    "18": 4,
    "20": 1,
    "22": 0,
    "36": 2,
    "47": 1,
    "58": 2,
    "69": 1,
    "77": 0,
    "88": 1,
    "90": 1,
    "99": 1,
    "01": 4,
    "05": 2,
    "06": 1,
    "09": 1,
    "12": 3,
    "34": 2,
    "49": 1,
}

DEFAULT_PAIR_SPACING = 2


@dataclass(frozen=True)
class GlyphAsset:
    digit: int
    image: Image.Image
    width: int
    height: int
    bbox: tuple[int, int, int, int]


def clean_generated_outputs() -> None:
    for path in [SINGLE_DIR, PAIR_DIR]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    HEADER_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(FONT_PATH), size)
    font.set_variation_by_axes([FONT_WEIGHT])
    return font


def digit_bbox(font: ImageFont.FreeTypeFont, digit: str) -> tuple[int, int, int, int]:
    scratch = Image.new("L", (512, 512), 0)
    draw = ImageDraw.Draw(scratch)
    return draw.textbbox((0, 0), digit, font=font)


def metrics_for_size(size: int) -> tuple[int, dict[str, tuple[int, int, int, int]]]:
    font = load_font(size)
    bboxes = {str(digit): digit_bbox(font, str(digit)) for digit in range(10)}
    top = min(bbox[1] for bbox in bboxes.values())
    bottom = max(bbox[3] for bbox in bboxes.values())
    return bottom - top, bboxes


def choose_font_size() -> tuple[int, dict[str, tuple[int, int, int, int]]]:
    best_size = 1
    best_bboxes: dict[str, tuple[int, int, int, int]] = {}
    for size in range(40, 220):
        height, bboxes = metrics_for_size(size)
        if height > RESOURCE_GLYPH_HEIGHT:
            continue
        widths = {digit: bbox[2] - bbox[0] for digit, bbox in bboxes.items()}
        max_pair_width = max(
            widths[str(left)] + pair_spacing(left, right) + widths[str(right)]
            for left in range(10)
            for right in range(10)
        )
        if max_pair_width <= ROW_WIDTH:
            best_size = size
            best_bboxes = bboxes
    if not best_bboxes:
        raise ValueError("No Red Hat Display Black font size fits the Pebble Time 2 row")
    return best_size, best_bboxes


def pair_spacing(left: int, right: int) -> int:
    return PAIR_SPACING.get(f"{left}{right}", DEFAULT_PAIR_SPACING)


def render_digit(font: ImageFont.FreeTypeFont, digit: int,
                 bbox: tuple[int, int, int, int],
                 global_top: int, global_bottom: int) -> GlyphAsset:
    width = bbox[2] - bbox[0]
    height = global_bottom - global_top
    image = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(image)
    draw.text((-bbox[0], -global_top), str(digit), font=font, fill=0)
    image = image.point(lambda value: 0 if value < 128 else 255, mode="1")
    return GlyphAsset(digit=digit, image=image, width=width, height=height, bbox=bbox)


def compose_pair(left: GlyphAsset, right: GlyphAsset) -> Image.Image:
    spacing = pair_spacing(left.digit, right.digit)
    width = left.width + spacing + right.width
    image = Image.new("1", (width, RESOURCE_GLYPH_HEIGHT), 1)
    y = (RESOURCE_GLYPH_HEIGHT - left.height) // 2
    image.paste(left.image, (0, y))
    image.paste(right.image, (left.width + spacing, y))
    return image


def save_assets(glyphs: list[GlyphAsset], font_size: int) -> dict:
    metrics = {
        "edition": "Red Hat Display Black",
        "source_font": str(FONT_PATH.relative_to(ROOT)),
        "font_weight_axis": FONT_WEIGHT,
        "font_size_px": font_size,
        "glyph_height": RESOURCE_GLYPH_HEIGHT,
        "default_pair_spacing": DEFAULT_PAIR_SPACING,
        "pair_spacing": {},
        "singles": {},
        "pairs": {},
    }

    for glyph in glyphs:
        path = SINGLE_DIR / f"squintless_font_single_{glyph.digit}.png"
        glyph.image.save(path)
        metrics["singles"][str(glyph.digit)] = {
            "file": str(path.relative_to(WATCHFACE_DIR)),
            "width": glyph.width,
            "height": glyph.height,
            "bbox": glyph.bbox,
        }

    for left in glyphs:
        for right in glyphs:
            key = f"{left.digit}{right.digit}"
            pair = compose_pair(left, right)
            path = PAIR_DIR / f"squintless_font_pair_{key}.png"
            pair.save(path)
            metrics["pairs"][key] = {
                "file": str(path.relative_to(WATCHFACE_DIR)),
                "width": pair.width,
                "height": pair.height,
                "spacing": pair_spacing(left.digit, right.digit),
            }
            if key in PAIR_SPACING:
                metrics["pair_spacing"][key] = PAIR_SPACING[key]

    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n")
    return metrics


def resource_name_for_single(digit: int) -> str:
    return f"IMAGE_SINGLE_{digit}"


def resource_name_for_pair(pair: str) -> str:
    return f"IMAGE_PAIR_{pair}"


def write_header(metrics: dict) -> None:
    single_widths = [metrics["singles"][str(digit)]["width"] for digit in range(10)]
    pair_widths = [metrics["pairs"][f"{left}{right}"]["width"] for left in range(10) for right in range(10)]
    pair_resources = [f"RESOURCE_ID_{resource_name_for_pair(f'{left}{right}')}" for left in range(10) for right in range(10)]

    lines = [
        "#pragma once",
        "",
        "#include <pebble.h>",
        "",
        f"#define SQUINTLESS_ASSET_HEIGHT {RESOURCE_GLYPH_HEIGHT}",
        "#define SQUINTLESS_PAIR_COUNT 100",
        "",
        "static const uint32_t SQUINTLESS_SINGLE_RESOURCE_IDS[10] = {",
    ]
    lines.extend(f"  RESOURCE_ID_{resource_name_for_single(digit)}," for digit in range(10))
    lines.extend([
        "};",
        "",
        "static const uint8_t SQUINTLESS_SINGLE_WIDTHS[10] = {",
        "  " + ", ".join(str(width) for width in single_widths),
        "};",
        "",
        "static const uint32_t SQUINTLESS_PAIR_RESOURCE_IDS[SQUINTLESS_PAIR_COUNT] = {",
    ])
    lines.extend(f"  {resource_id}," for resource_id in pair_resources)
    lines.extend([
        "};",
        "",
        "static const uint8_t SQUINTLESS_PAIR_WIDTHS[SQUINTLESS_PAIR_COUNT] = {",
    ])
    for row in range(10):
        values = pair_widths[row * 10:(row + 1) * 10]
        lines.append("  " + ", ".join(str(value) for value in values) + ",")
    lines.extend([
        "};",
        "",
        "static inline uint8_t squintless_pair_index(char tens, char ones) {",
        "  return ((uint8_t)(tens - '0') * 10) + (uint8_t)(ones - '0');",
        "}",
        "",
    ])
    HEADER_PATH.write_text("\n".join(lines))


def update_package_json(metrics: dict) -> None:
    package = json.loads(PACKAGE_PATH.read_text())
    package["name"] = "squintless-font-edition"
    package["version"] = "1.0.1"
    package["pebble"]["displayName"] = "Squintless Font"
    package["pebble"]["uuid"] = "fd3d9535-e58f-4d8f-b75c-750e8bbd0c10"

    media = []
    for digit in range(10):
        resource_file = str(Path(metrics["singles"][str(digit)]["file"]).relative_to("resources"))
        media.append({
            "type": "bitmap",
            "name": resource_name_for_single(digit),
            "file": resource_file,
        })
    for pair in sorted(metrics["pairs"]):
        resource_file = str(Path(metrics["pairs"][pair]["file"]).relative_to("resources"))
        media.append({
            "type": "bitmap",
            "name": resource_name_for_pair(pair),
            "file": resource_file,
        })
    package["pebble"]["resources"]["media"] = media
    PACKAGE_PATH.write_text(json.dumps(package, indent=2) + "\n")


def assert_pair_widths(metrics: dict) -> None:
    too_wide = [
        (pair, data["width"])
        for pair, data in metrics["pairs"].items()
        if data["width"] > ROW_WIDTH
    ]
    if too_wide:
        formatted = ", ".join(f"{pair}:{width}" for pair, width in too_wide)
        raise ValueError(f"Generated pair resources exceed row width: {formatted}")


def main() -> None:
    clean_generated_outputs()
    font_size, bboxes = choose_font_size()
    font = load_font(font_size)
    global_top = min(bbox[1] for bbox in bboxes.values())
    global_bottom = max(bbox[3] for bbox in bboxes.values())
    glyphs = [
        render_digit(font, digit, bboxes[str(digit)], global_top, global_bottom)
        for digit in range(10)
    ]
    metrics = save_assets(glyphs, font_size)
    assert_pair_widths(metrics)
    write_header(metrics)
    update_package_json(metrics)


if __name__ == "__main__":
    main()
