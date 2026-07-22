#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_WATCHFACE = ROOT / "watchface-russo"
PRODUCTION_ICON = ROOT / "watchface" / "resources" / "images" / "menu_icon.png"
PRODUCTION_UUID = "c68b0184-aad6-4bdc-9c72-d18a13fc1f06"

PACKAGE_DESCRIPTION = (
    "Designed for your aging eyes, not your ego. Squintless is an accessibility-first "
    "Pebble Time 2 watch face with a large temporary date glance."
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


def copy_source_project(destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)

    shutil.copytree(
        SOURCE_WATCHFACE,
        destination,
        ignore=shutil.ignore_patterns("build", "previews", "__pycache__", "*.pyc"),
    )


def patch_package_json(destination: Path, version: str) -> None:
    package_path = destination / "package.json"
    package = json.loads(package_path.read_text())

    package["name"] = "squintless"
    package["author"] = "Mangla & Co LLC"
    package["version"] = version
    package["license"] = "MIT"
    package["keywords"] = PACKAGE_KEYWORDS
    package["description"] = PACKAGE_DESCRIPTION
    package["private"] = True

    pebble = package["pebble"]
    pebble["displayName"] = "Squintless"
    pebble["uuid"] = PRODUCTION_UUID

    media = [
        item
        for item in pebble["resources"]["media"]
        if not item.get("menuIcon") and item.get("name") != "IMAGE_MENU_ICON"
    ]
    media.insert(0, {
        "type": "bitmap",
        "name": "IMAGE_MENU_ICON",
        "file": "images/menu_icon.png",
        "menuIcon": True,
    })
    pebble["resources"]["media"] = media

    icon_destination = destination / "resources" / "images" / "menu_icon.png"
    icon_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PRODUCTION_ICON, icon_destination)

    package_path.write_text(json.dumps(package, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="1.1.0")
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path("/private/tmp/squintless-app-store-1.1.0"),
    )
    args = parser.parse_args()

    destination = args.destination
    copy_source_project(destination)
    patch_package_json(destination, args.version)
    print(destination)


if __name__ == "__main__":
    main()
