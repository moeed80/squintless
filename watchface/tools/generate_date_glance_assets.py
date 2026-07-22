#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONT_PATH = ROOT / "typeface" / "fonts" / "russo-one" / "RussoOne-Regular.ttf"

MAX_FONT_SIZE = 180
MONTH_TRACKING = -2
DAY_TRACKING = -6

MONTHS = [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
]

DAYS = [f"{day:02d}" for day in range(1, 32)]


@dataclass(frozen=True)
class DisplayProfile:
    key: str
    display_width: int
    display_height: int
    row_width: int
    resource_height: int
    file_suffix: str


DISPLAY_PROFILES = [
    DisplayProfile(
        key="emery_200x228",
        display_width=200,
        display_height=228,
        row_width=196,
        resource_height=100,
        file_suffix="",
    ),
    DisplayProfile(
        key="rect_144x168",
        display_width=144,
        display_height=168,
        row_width=140,
        resource_height=74,
        file_suffix="~144w~168h",
    ),
]
DEFAULT_PROFILE_KEY = "emery_200x228"


@dataclass(frozen=True)
class RenderedAsset:
    text: str
    image: Image.Image
    width: int
    height: int
    font_size: int
    ink_bbox: tuple[int, int, int, int]


def text_bbox(font: ImageFont.FreeTypeFont, text: str, tracking: int) -> tuple[int, int, int, int]:
    draw = ImageDraw.Draw(Image.new("L", (1, 1)))
    boxes = [draw.textbbox((0, 0), char, font=font) for char in text]
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = sum(box[2] - box[0] for box in boxes) + tracking * (len(text) - 1)
    bottom = max(box[3] for box in boxes)
    return left, top, right, bottom


def choose_font_size(profile: DisplayProfile, labels: list[str], tracking: int) -> int:
    for size in range(MAX_FONT_SIZE, 1, -1):
        font = ImageFont.truetype(str(FONT_PATH), size=size)
        if all(fits(profile, font, label, tracking) for label in labels):
            return size
    raise ValueError("Could not fit date glance labels")


def fits(profile: DisplayProfile, font: ImageFont.FreeTypeFont,
         text: str, tracking: int) -> bool:
    left, top, right, bottom = text_bbox(font, text, tracking)
    return right - left <= profile.row_width and bottom - top <= profile.resource_height


def render_label(profile: DisplayProfile, font: ImageFont.FreeTypeFont,
                 text: str, tracking: int) -> RenderedAsset:
    draw = ImageDraw.Draw(Image.new("L", (1, 1)))
    boxes = [draw.textbbox((0, 0), char, font=font) for char in text]
    widths = [box[2] - box[0] for box in boxes]
    top = min(box[1] for box in boxes)
    bottom = max(box[3] for box in boxes)
    width = max(1, sum(widths) + tracking * (len(text) - 1))
    height = max(1, bottom - top)

    scratch = Image.new("L", (width + 8, height + 8), 255)
    scratch_draw = ImageDraw.Draw(scratch)
    x = 4
    for char, box, char_width in zip(text, boxes, widths):
        scratch_draw.text((x - box[0], 4 - top), char, font=font, fill=0)
        x += char_width + tracking

    thresholded = scratch.point(lambda value: 0 if value < 128 else 255, mode="L")
    black_mask = thresholded.point(lambda value: 255 if value == 0 else 0, mode="L")
    ink_bbox = black_mask.getbbox()
    if ink_bbox is None:
        raise ValueError(f"Font render for {text} produced no pixels")

    cropped = thresholded.crop(ink_bbox)
    output = Image.new("1", (cropped.width, profile.resource_height), 1)
    y = (profile.resource_height - cropped.height) // 2
    output.paste(cropped.point(lambda value: 0 if value < 128 else 255, mode="1"), (0, y))
    return RenderedAsset(
        text=text,
        image=output,
        width=output.width,
        height=output.height,
        font_size=font.size,
        ink_bbox=ink_bbox,
    )


def render_label_at_max_size(profile: DisplayProfile, text: str, tracking: int) -> RenderedAsset:
    font_size = choose_font_size(profile, [text], tracking)
    font = ImageFont.truetype(str(FONT_PATH), size=font_size)
    return render_label(profile, font, text, tracking)


def month_resource_name(month: str) -> str:
    return f"IMAGE_DATE_MONTH_{month}"


def day_resource_name(day: str) -> str:
    return f"IMAGE_DATE_DAY_{day}"


def file_stem_with_suffix(stem: str, profile: DisplayProfile) -> str:
    return f"{stem}{profile.file_suffix}.png"


def month_file(month: str, profile: DisplayProfile) -> Path:
    return (
        Path("resources")
        / "images"
        / "date"
        / "months"
        / file_stem_with_suffix(f"squintless_date_month_{month.lower()}", profile)
    )


def day_file(day: str, profile: DisplayProfile) -> Path:
    return (
        Path("resources")
        / "images"
        / "date"
        / "days"
        / file_stem_with_suffix(f"squintless_date_day_{day}", profile)
    )


def write_assets(watchface_dir: Path,
                 profile_assets: dict[str, tuple[list[RenderedAsset], list[RenderedAsset]]]) -> dict:
    month_dir = watchface_dir / "resources" / "images" / "date" / "months"
    day_dir = watchface_dir / "resources" / "images" / "date" / "days"
    generated_dir = watchface_dir / "src" / "c" / "generated"

    month_dir.mkdir(parents=True, exist_ok=True)
    day_dir.mkdir(parents=True, exist_ok=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "source_font": str(FONT_PATH.relative_to(ROOT)),
        "license": "SIL Open Font License 1.1",
        "month_tracking": MONTH_TRACKING,
        "day_tracking": DAY_TRACKING,
        "profiles": {},
    }

    for profile in DISPLAY_PROFILES:
        month_assets, day_assets = profile_assets[profile.key]
        profile_metrics = {
            "display_width": profile.display_width,
            "display_height": profile.display_height,
            "asset_height": profile.resource_height,
            "row_width": profile.row_width,
            "file_suffix": profile.file_suffix,
            "months": {},
            "days": {},
        }

        for asset in month_assets:
            path = watchface_dir / month_file(asset.text, profile)
            asset.image.save(path)
            profile_metrics["months"][asset.text] = {
                "file": str(path.relative_to(watchface_dir)),
                "width": asset.width,
                "height": asset.height,
                "font_size_px": asset.font_size,
                "ink_bbox": asset.ink_bbox,
            }

        for asset in day_assets:
            path = watchface_dir / day_file(asset.text, profile)
            asset.image.save(path)
            profile_metrics["days"][asset.text] = {
                "file": str(path.relative_to(watchface_dir)),
                "width": asset.width,
                "height": asset.height,
                "font_size_px": asset.font_size,
                "ink_bbox": asset.ink_bbox,
            }

        metrics["profiles"][profile.key] = profile_metrics

    default_metrics = metrics["profiles"][DEFAULT_PROFILE_KEY]
    metrics["asset_height"] = default_metrics["asset_height"]
    metrics["row_width"] = default_metrics["row_width"]
    metrics["months"] = default_metrics["months"]
    metrics["days"] = default_metrics["days"]

    (generated_dir / "squintless_date_metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n"
    )
    return metrics


def write_header(watchface_dir: Path) -> None:
    lines = [
        "#pragma once",
        "",
        "#include <pebble.h>",
        "",
        "#define SQUINTLESS_DATE_MONTH_COUNT 12",
        "#define SQUINTLESS_DATE_DAY_COUNT 31",
        "",
        "static const uint32_t SQUINTLESS_DATE_MONTH_RESOURCE_IDS[SQUINTLESS_DATE_MONTH_COUNT] = {",
    ]
    lines.extend(f"  RESOURCE_ID_{month_resource_name(month)}," for month in MONTHS)
    lines.extend([
        "};",
        "",
        "static const uint32_t SQUINTLESS_DATE_DAY_RESOURCE_IDS[SQUINTLESS_DATE_DAY_COUNT] = {",
    ])
    lines.extend(f"  RESOURCE_ID_{day_resource_name(day)}," for day in DAYS)
    lines.extend([
        "};",
        "",
    ])
    (watchface_dir / "src" / "c" / "generated" / "squintless_date_assets.h").write_text(
        "\n".join(lines)
    )


def update_package_json(watchface_dir: Path, metrics: dict) -> None:
    package_path = watchface_dir / "package.json"
    package = json.loads(package_path.read_text())
    media = package["pebble"]["resources"]["media"]
    media = [
        item
        for item in media
        if not item.get("name", "").startswith("IMAGE_DATE_MONTH_")
        and not item.get("name", "").startswith("IMAGE_DATE_DAY_")
    ]

    for month in MONTHS:
        media.append({
            "type": "bitmap",
            "name": month_resource_name(month),
            "file": str(Path(metrics["months"][month]["file"]).relative_to("resources")),
        })

    for day in DAYS:
        media.append({
            "type": "bitmap",
            "name": day_resource_name(day),
            "file": str(Path(metrics["days"][day]["file"]).relative_to("resources")),
        })

    package["pebble"]["resources"]["media"] = media
    package_path.write_text(json.dumps(package, indent=2) + "\n")


def generate_for_watchface(watchface_dir: Path) -> None:
    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Russo One font is missing: {FONT_PATH}")

    profile_assets = {}
    for profile in DISPLAY_PROFILES:
        month_assets = [
            render_label_at_max_size(profile, month, MONTH_TRACKING)
            for month in MONTHS
        ]
        day_assets = [
            render_label_at_max_size(profile, day, DAY_TRACKING)
            for day in DAYS
        ]
        profile_assets[profile.key] = (month_assets, day_assets)
    metrics = write_assets(watchface_dir, profile_assets)
    write_header(watchface_dir)
    update_package_json(watchface_dir, metrics)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "target",
        nargs="?",
        default="watchface",
        choices=["watchface", "watchface-russo", "all"],
    )
    args = parser.parse_args()

    targets = ["watchface", "watchface-russo"] if args.target == "all" else [args.target]
    for target in targets:
        generate_for_watchface(ROOT / target)


if __name__ == "__main__":
    main()
