#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]

MAX_FONT_SIZE = 260

PACKAGE_DESCRIPTION = (
    "Experimental Squintless variant for rectangular Pebble readability testing."
)
PACKAGE_KEYWORDS = [
    "pebble-watchface",
    "accessibility",
    "large-digits",
    "readability",
    "low-vision",
    "rectangular-pebble",
    "pebble-time-2",
    "experiment",
]

RED_HAT_PAIR_SPACING = {
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
    "27": 1,
    "34": 2,
    "49": 1,
}

RUSSO_PAIR_SPACING = {
    "00": 0,
    "08": -1,
    "10": 3,
    "11": 13,
    "18": 2,
    "20": 0,
    "22": -1,
    "27": 0,
    "36": -1,
    "47": 0,
    "58": -1,
    "69": -1,
    "77": 0,
    "88": -1,
    "90": 0,
    "99": 0,
    "01": 3,
    "05": 0,
    "06": -1,
    "09": 0,
    "12": 2,
    "34": -1,
    "49": 0,
}


@dataclass(frozen=True)
class DisplayProfile:
    key: str
    display_width: int
    display_height: int
    row_width: int
    asset_height: int
    file_suffix: str


DISPLAY_PROFILES = [
    DisplayProfile(
        key="emery_200x228",
        display_width=200,
        display_height=228,
        row_width=196,
        asset_height=100,
        file_suffix="",
    ),
    DisplayProfile(
        key="rect_144x168",
        display_width=144,
        display_height=168,
        row_width=140,
        asset_height=74,
        file_suffix="~144w~168h",
    ),
]
DEFAULT_PROFILE_KEY = "emery_200x228"


@dataclass(frozen=True)
class FontVariant:
    key: str
    edition_name: str
    watchface_dir: Path
    font_path: Path
    resource_prefix: str
    package_name: str
    display_name: str
    uuid: str
    output_pbw_name: str
    default_pair_spacing: int
    pair_spacing: dict[str, int]
    target_platforms: list[str]
    font_weight_axis: int | None = None


VARIANTS = {
    "redhat": FontVariant(
        key="redhat",
        edition_name="Squintless Red Hat Edition",
        watchface_dir=ROOT / "watchface-redhat",
        font_path=ROOT / "typeface" / "fonts" / "red-hat-display" / "RedHatDisplay-wght.ttf",
        resource_prefix="squintless_redhat",
        package_name="squintless-redhat",
        display_name="Squintless Red Hat",
        uuid="fd3d9535-e58f-4d8f-b75c-750e8bbd0c10",
        output_pbw_name="watchface-redhat.pbw",
        default_pair_spacing=2,
        pair_spacing=RED_HAT_PAIR_SPACING,
        target_platforms=["emery"],
        font_weight_axis=900,
    ),
    "russo": FontVariant(
        key="russo",
        edition_name="Squintless Russo Edition",
        watchface_dir=ROOT / "watchface-russo",
        font_path=ROOT / "typeface" / "fonts" / "russo-one" / "RussoOne-Regular.ttf",
        resource_prefix="squintless_russo",
        package_name="squintless-russo",
        display_name="Squintless Russo",
        uuid="1ac8a616-0d03-52ef-bcb2-afc8d993873b",
        output_pbw_name="watchface-russo.pbw",
        default_pair_spacing=0,
        pair_spacing=RUSSO_PAIR_SPACING,
        target_platforms=["aplite", "basalt", "diorite", "emery", "flint"],
    ),
}


@dataclass(frozen=True)
class RenderedAsset:
    text: str
    image: Image.Image
    width: int
    height: int
    font_size: int
    spacing: int | None
    ink_bbox: tuple[int, int, int, int]


def load_font(variant: FontVariant, size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(variant.font_path), size)
    if variant.font_weight_axis is not None:
        font.set_variation_by_axes([variant.font_weight_axis])
    return font


def spacing_for(variant: FontVariant, text: str) -> int:
    return variant.pair_spacing.get(text, variant.default_pair_spacing)


def digit_bbox(font: ImageFont.FreeTypeFont, digit: str) -> tuple[int, int, int, int]:
    scratch = Image.new("L", (512, 512), 255)
    draw = ImageDraw.Draw(scratch)
    return draw.textbbox((0, 0), digit, font=font)


def render_text_at_size(variant: FontVariant, profile: DisplayProfile,
                        text: str, size: int) -> tuple[Image.Image, tuple[int, int, int, int]]:
    font = load_font(variant, size)
    bboxes = [digit_bbox(font, digit) for digit in text]
    top = min(bbox[1] for bbox in bboxes)
    bottom = max(bbox[3] for bbox in bboxes)
    widths = [bbox[2] - bbox[0] for bbox in bboxes]
    spacing = spacing_for(variant, text) if len(text) == 2 else 0
    width = max(1, sum(widths) + max(0, len(text) - 1) * spacing)
    height = max(1, bottom - top)

    # Extra side padding protects against antialiasing fringes before final thresholding.
    scratch = Image.new("L", (width + 8, height + 8), 255)
    draw = ImageDraw.Draw(scratch)
    x = 4
    for digit, bbox, digit_width in zip(text, bboxes, widths):
        draw.text((x - bbox[0], 4 - top), digit, font=font, fill=0)
        x += digit_width + spacing

    ink = scratch.point(lambda value: 0 if value < 128 else 255, mode="L")
    black_mask = ink.point(lambda value: 255 if value == 0 else 0, mode="L")
    bbox = black_mask.getbbox()
    if bbox is None:
        raise ValueError(f"Font render for {text} produced no pixels")
    return ink.crop(bbox), bbox


def fits(variant: FontVariant, profile: DisplayProfile, text: str, size: int) -> bool:
    cropped, _bbox = render_text_at_size(variant, profile, text, size)
    return cropped.width <= profile.row_width and cropped.height <= profile.asset_height


def choose_font_size(variant: FontVariant, profile: DisplayProfile, text: str) -> int:
    lo = 1
    hi = MAX_FONT_SIZE
    best = 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if fits(variant, profile, text, mid):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def render_asset(variant: FontVariant, profile: DisplayProfile, text: str) -> RenderedAsset:
    font_size = choose_font_size(variant, profile, text)
    cropped, bbox = render_text_at_size(variant, profile, text, font_size)
    output = Image.new("1", (cropped.width, profile.asset_height), 1)
    y = (profile.asset_height - cropped.height) // 2
    one_bit = cropped.point(lambda value: 0 if value < 128 else 255, mode="1")
    output.paste(one_bit, (0, y))
    return RenderedAsset(
        text=text,
        image=output,
        width=output.width,
        height=output.height,
        font_size=font_size,
        spacing=spacing_for(variant, text) if len(text) == 2 else None,
        ink_bbox=bbox,
    )


def clean_generated_outputs(variant: FontVariant) -> None:
    for path in [
        variant.watchface_dir / "resources" / "images" / "singles",
        variant.watchface_dir / "resources" / "images" / "pairs",
    ]:
        path.mkdir(parents=True, exist_ok=True)
        for tagged_asset in path.glob("*~*.png"):
            tagged_asset.unlink()
    (variant.watchface_dir / "src" / "c" / "generated").mkdir(parents=True, exist_ok=True)


def resource_name_for_single(digit: int) -> str:
    return f"IMAGE_SINGLE_{digit}"


def resource_name_for_pair(pair: str) -> str:
    return f"IMAGE_PAIR_{pair}"


def file_stem_with_suffix(stem: str, profile: DisplayProfile) -> str:
    return f"{stem}{profile.file_suffix}.png"


def save_or_preserve_asset(path: Path, profile: DisplayProfile,
                           asset: RenderedAsset) -> tuple[int, int]:
    if profile.key == DEFAULT_PROFILE_KEY and path.exists():
        existing = Image.open(path)
        return existing.width, existing.height

    asset.image.save(path)
    return asset.width, asset.height


def save_assets(variant: FontVariant,
                profile_assets: dict[str, tuple[list[RenderedAsset], list[RenderedAsset]]]) -> dict:
    single_dir = variant.watchface_dir / "resources" / "images" / "singles"
    pair_dir = variant.watchface_dir / "resources" / "images" / "pairs"
    metrics = {
        "edition": variant.edition_name,
        "source_font": str(variant.font_path.relative_to(ROOT)),
        "font_weight_axis": variant.font_weight_axis,
        "default_pair_spacing": variant.default_pair_spacing,
        "pair_spacing": dict(sorted(variant.pair_spacing.items())),
        "profiles": {},
    }

    for profile in DISPLAY_PROFILES:
        singles, pairs = profile_assets[profile.key]
        profile_metrics = {
            "display_width": profile.display_width,
            "display_height": profile.display_height,
            "asset_height": profile.asset_height,
            "row_width": profile.row_width,
            "file_suffix": profile.file_suffix,
            "singles": {},
            "pairs": {},
        }

        for asset in singles:
            path = single_dir / file_stem_with_suffix(
                f"{variant.resource_prefix}_single_{asset.text}",
                profile,
            )
            width, height = save_or_preserve_asset(path, profile, asset)
            profile_metrics["singles"][asset.text] = {
                "file": str(path.relative_to(variant.watchface_dir)),
                "width": width,
                "height": height,
                "font_size_px": asset.font_size,
                "ink_bbox": asset.ink_bbox,
            }

        for asset in pairs:
            path = pair_dir / file_stem_with_suffix(
                f"{variant.resource_prefix}_pair_{asset.text}",
                profile,
            )
            width, height = save_or_preserve_asset(path, profile, asset)
            profile_metrics["pairs"][asset.text] = {
                "file": str(path.relative_to(variant.watchface_dir)),
                "width": width,
                "height": height,
                "font_size_px": asset.font_size,
                "spacing": asset.spacing,
                "ink_bbox": asset.ink_bbox,
            }

        metrics["profiles"][profile.key] = profile_metrics

    default_metrics = metrics["profiles"][DEFAULT_PROFILE_KEY]
    metrics["asset_height"] = default_metrics["asset_height"]
    metrics["row_width"] = default_metrics["row_width"]
    metrics["singles"] = default_metrics["singles"]
    metrics["pairs"] = default_metrics["pairs"]

    metrics_path = variant.watchface_dir / "src" / "c" / "generated" / "squintless_typeface_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n")
    return metrics


def write_header(variant: FontVariant, metrics: dict) -> None:
    header_path = variant.watchface_dir / "src" / "c" / "generated" / "squintless_typeface_assets.h"
    single_widths = [metrics["singles"][str(digit)]["width"] for digit in range(10)]
    pair_widths = [metrics["pairs"][f"{left}{right}"]["width"] for left in range(10) for right in range(10)]
    pair_spacings = [
        spacing_for(variant, f"{left}{right}")
        for left in range(10)
        for right in range(10)
    ]
    pair_resources = [
        f"RESOURCE_ID_{resource_name_for_pair(f'{left}{right}')}"
        for left in range(10)
        for right in range(10)
    ]

    lines = [
        "#pragma once",
        "",
        "#include <pebble.h>",
        "",
        f"#define SQUINTLESS_ASSET_HEIGHT {metrics['asset_height']}",
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
        "static const int8_t SQUINTLESS_PAIR_SPACINGS[SQUINTLESS_PAIR_COUNT] = {",
    ])
    for row in range(10):
        values = pair_spacings[row * 10:(row + 1) * 10]
        lines.append("  " + ", ".join(str(value) for value in values) + ",")
    lines.extend([
        "};",
        "",
        "#if !defined(PBL_PLATFORM_APLITE)",
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
        "#endif",
        "",
        "static inline uint8_t squintless_pair_index(char tens, char ones) {",
        "  return ((uint8_t)(tens - '0') * 10) + (uint8_t)(ones - '0');",
        "}",
        "",
        "static inline int8_t squintless_pair_spacing(char tens, char ones) {",
        "  return SQUINTLESS_PAIR_SPACINGS[squintless_pair_index(tens, ones)];",
        "}",
        "",
    ])
    header_path.write_text("\n".join(lines))


def update_package_json(variant: FontVariant, metrics: dict) -> None:
    package_path = variant.watchface_dir / "package.json"
    package = json.loads(package_path.read_text())
    package["name"] = variant.package_name
    package["author"] = "Mangla & Co LLC"
    package["version"] = "1.0.0"
    package["license"] = "MIT"
    package["description"] = PACKAGE_DESCRIPTION
    package["keywords"] = PACKAGE_KEYWORDS
    package["private"] = True

    package["pebble"]["displayName"] = variant.display_name
    package["pebble"]["uuid"] = variant.uuid
    package["pebble"]["sdkVersion"] = "3"
    package["pebble"]["enableMultiJS"] = True
    package["pebble"]["targetPlatforms"] = variant.target_platforms
    package["pebble"]["watchapp"] = {"watchface": True}
    package["pebble"]["messageKeys"] = []

    media = [
        item
        for item in package["pebble"]["resources"].get("media", [])
        if not item.get("name", "").startswith("IMAGE_SINGLE_")
        and not item.get("name", "").startswith("IMAGE_PAIR_")
    ]
    for digit in range(10):
        resource_file = str(Path(metrics["singles"][str(digit)]["file"]).relative_to("resources"))
        media.append({
            "type": "bitmap",
            "name": resource_name_for_single(digit),
            "file": resource_file,
        })
    for pair in sorted(metrics["pairs"]):
        resource_file = str(Path(metrics["pairs"][pair]["file"]).relative_to("resources"))
        item = {
            "type": "bitmap",
            "name": resource_name_for_pair(pair),
            "file": resource_file,
        }
        pair_targets = [platform for platform in variant.target_platforms if platform != "aplite"]
        if pair_targets != variant.target_platforms:
            item["targetPlatforms"] = pair_targets
        media.append(item)
    package["pebble"]["resources"]["media"] = media
    package_path.write_text(json.dumps(package, indent=2) + "\n")


def assert_assets(metrics: dict) -> None:
    too_wide = []
    too_tall = []
    for profile_key, profile in metrics["profiles"].items():
        row_width = profile["row_width"]
        asset_height = profile["asset_height"]
        too_wide.extend(
            (profile_key, pair, data["width"])
            for pair, data in profile["pairs"].items()
            if data["width"] > row_width
        )
        too_tall.extend(
            (profile_key, pair, data["height"])
            for pair, data in profile["pairs"].items()
            if data["height"] > asset_height
        )
    if too_wide:
        formatted = ", ".join(f"{profile}:{pair}:{width}" for profile, pair, width in too_wide)
        raise ValueError(f"Generated pair resources exceed row width: {formatted}")
    if too_tall:
        formatted = ", ".join(f"{profile}:{pair}:{height}" for profile, pair, height in too_tall)
        raise ValueError(f"Generated pair resources exceed asset height: {formatted}")


def generate_variant(variant: FontVariant) -> None:
    clean_generated_outputs(variant)
    profile_assets = {}
    for profile in DISPLAY_PROFILES:
        singles = [render_asset(variant, profile, str(digit)) for digit in range(10)]
        pairs = [
            render_asset(variant, profile, f"{left}{right}")
            for left in range(10)
            for right in range(10)
        ]
        profile_assets[profile.key] = (singles, pairs)
    metrics = save_assets(variant, profile_assets)
    assert_assets(metrics)
    write_header(variant, metrics)
    update_package_json(variant, metrics)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("variant", choices=[*VARIANTS.keys(), "all"])
    args = parser.parse_args()

    variants = VARIANTS.values() if args.variant == "all" else [VARIANTS[args.variant]]
    for variant in variants:
        generate_variant(variant)


if __name__ == "__main__":
    main()
