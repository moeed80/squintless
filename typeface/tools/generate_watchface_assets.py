#!/usr/bin/env python3
from __future__ import annotations

import io
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
TYPEFACE_DIR = ROOT / "typeface" / "artifacts"
WATCHFACE_DIR = ROOT / "watchface"
RESOURCE_DIR = WATCHFACE_DIR / "resources" / "images"
SINGLE_DIR = RESOURCE_DIR / "singles"
PAIR_DIR = RESOURCE_DIR / "pairs"
HEADER_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_assets.h"
METRICS_PATH = WATCHFACE_DIR / "src" / "c" / "generated" / "squintless_typeface_metrics.json"
PACKAGE_PATH = WATCHFACE_DIR / "package.json"

PACKAGE_DESCRIPTION = (
    "Designed for your aging eyes, not your ego. "
    "Squintless is an accessibility-first Pebble Time 2 watch face built for instant readability."
)
PACKAGE_KEYWORDS = [
    "pebble-watchface",
    "accessibility",
    "large-digits",
    "readability",
    "low-vision",
    "emery",
    "pebble-time-2",
]
MENU_ICON_FILE = "images/menu_icon.png"

CANONICAL_TOP = 55
CANONICAL_BASELINE = 945
CANONICAL_VISIBLE_HEIGHT = CANONICAL_BASELINE - CANONICAL_TOP
RESOURCE_GLYPH_HEIGHT = 100
RASTER_SCALE = 4

PAIR_SPACING = {
    "11": 14,
    "10": 5,
    "18": 5,
    "08": 2,
    "88": 2,
    "20": 2,
    "22": 2,
    "36": 4,
    "49": 1,
    "58": 5,
    "69": 1,
    "90": 1,
    "01": 5,
    "05": 3,
    "06": 2,
    "09": 1,
    "12": 4,
    "34": 3,
}

DEFAULT_PAIR_SPACING = 2


@dataclass(frozen=True)
class GlyphAsset:
    digit: int
    image: Image.Image
    width: int
    height: int
    visible_bounds: tuple[int, int, int, int]
    source_svg: Path


def clean_generated_outputs() -> None:
    for path in [SINGLE_DIR, PAIR_DIR]:
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    HEADER_PATH.parent.mkdir(parents=True, exist_ok=True)


def render_svg_to_rgba(svg_path: Path) -> Image.Image:
    png_bytes = cairosvg.svg2png(
        url=str(svg_path),
        output_width=1000 * RASTER_SCALE,
        output_height=1000 * RASTER_SCALE,
    )
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    thresholded = alpha.point(lambda value: 255 if value >= 128 else 0)
    bbox = thresholded.getbbox()
    if bbox is None:
      raise ValueError("SVG rendered without visible pixels")
    return bbox


def monochrome_from_alpha(cropped: Image.Image, target_height: int) -> Image.Image:
    scale = target_height / cropped.height
    target_width = max(1, round(cropped.width * scale))
    alpha = cropped.getchannel("A").resize((target_width, target_height), Image.Resampling.LANCZOS)
    mask = alpha.point(lambda value: 0 if value >= 128 else 255, mode="1")
    output = Image.new("1", (target_width, target_height), 1)
    output.paste(0, (0, 0), mask.point(lambda value: 255 if value == 0 else 0, mode="1"))
    return output


def load_glyph(digit: int) -> GlyphAsset:
    svg_path = TYPEFACE_DIR / f"squintless-{digit}-canonical" / f"squintless-{digit}.svg"
    rendered = render_svg_to_rgba(svg_path)
    x0, _y0, x1, _y1 = alpha_bbox(rendered)
    y0 = CANONICAL_TOP * RASTER_SCALE
    y1 = CANONICAL_BASELINE * RASTER_SCALE
    cropped = rendered.crop((x0, y0, x1, y1))
    image = monochrome_from_alpha(cropped, RESOURCE_GLYPH_HEIGHT)
    return GlyphAsset(
        digit=digit,
        image=image,
        width=image.width,
        height=image.height,
        visible_bounds=(x0 // RASTER_SCALE, CANONICAL_TOP, x1 // RASTER_SCALE, CANONICAL_BASELINE),
        source_svg=svg_path.relative_to(ROOT),
    )


def pair_spacing(left: int, right: int) -> int:
    return PAIR_SPACING.get(f"{left}{right}", DEFAULT_PAIR_SPACING)


def compose_pair(left: GlyphAsset, right: GlyphAsset) -> Image.Image:
    spacing = pair_spacing(left.digit, right.digit)
    width = left.width + spacing + right.width
    image = Image.new("1", (width, RESOURCE_GLYPH_HEIGHT), 1)
    image.paste(left.image, (0, 0))
    image.paste(right.image, (left.width + spacing, 0))
    return image


def save_assets(glyphs: list[GlyphAsset]) -> dict:
    metrics = {
        "glyph_height": RESOURCE_GLYPH_HEIGHT,
        "default_pair_spacing": DEFAULT_PAIR_SPACING,
        "pair_spacing": {},
        "singles": {},
        "pairs": {},
    }

    for glyph in glyphs:
        path = SINGLE_DIR / f"squintless_single_{glyph.digit}.png"
        glyph.image.save(path)
        metrics["singles"][str(glyph.digit)] = {
            "file": str(path.relative_to(WATCHFACE_DIR)),
            "width": glyph.width,
            "height": glyph.height,
            "source_svg": str(glyph.source_svg),
            "visible_bounds": glyph.visible_bounds,
        }

    for left in glyphs:
        for right in glyphs:
            pair = compose_pair(left, right)
            key = f"{left.digit}{right.digit}"
            path = PAIR_DIR / f"squintless_pair_{key}.png"
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
    package["name"] = "squintless"
    package["author"] = "Mangla & Co LLC"
    package["version"] = "1.0.0"
    package["license"] = "MIT"
    package["description"] = PACKAGE_DESCRIPTION
    package["keywords"] = PACKAGE_KEYWORDS
    package["private"] = True

    package["pebble"]["displayName"] = "Squintless"
    package["pebble"]["uuid"] = "c68b0184-aad6-4bdc-9c72-d18a13fc1f06"
    package["pebble"]["sdkVersion"] = "3"
    package["pebble"]["enableMultiJS"] = True
    package["pebble"]["targetPlatforms"] = ["emery"]
    package["pebble"]["watchapp"] = {"watchface": True}
    package["pebble"]["messageKeys"] = []

    media = []
    if (WATCHFACE_DIR / "resources" / MENU_ICON_FILE).exists():
        media.append({
            "type": "bitmap",
            "name": "IMAGE_MENU_ICON",
            "file": MENU_ICON_FILE,
            "menuIcon": True,
        })
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
        if data["width"] > 196
    ]
    if too_wide:
        formatted = ", ".join(f"{pair}:{width}" for pair, width in too_wide)
        raise ValueError(f"Generated pair resources exceed row width: {formatted}")


def main() -> None:
    clean_generated_outputs()
    glyphs = [load_glyph(digit) for digit in range(10)]
    metrics = save_assets(glyphs)
    assert_pair_widths(metrics)
    write_header(metrics)
    update_package_json(metrics)


if __name__ == "__main__":
    main()
