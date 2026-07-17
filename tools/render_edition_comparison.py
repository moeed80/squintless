#!/usr/bin/env python3
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "comparison" / "screenshots"

STATES = [
    ("08-36", 75),
    ("11-11", 50),
    ("12-34", 66),
    ("20-58", 30),
    ("01-05", 15),
    ("06-49", 8),
    ("09-06", 10),
    ("18-18", 85),
    ("22-22", 40),
]


def combine(svg_path: Path, font_path: Path, out_path: Path) -> None:
    svg = Image.open(svg_path).convert("L")
    font = Image.open(font_path).convert("L")
    gap = 8
    canvas = Image.new("L", (svg.width + gap + font.width, svg.height), 255)
    canvas.paste(svg, (0, 0))
    canvas.paste(font, (svg.width + gap, 0))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)


def main() -> None:
    for slug, battery in STATES:
        svg_path = ROOT / "watchface" / "screenshots" / f"squintless-canonical-{slug}-battery-{battery}.png"
        font_path = ROOT / "watchface-font" / "screenshots" / f"squintless-font-{slug}-battery-{battery}.png"
        out_path = OUT_DIR / f"squintless-svg-vs-font-{slug}-battery-{battery}.png"
        combine(svg_path, font_path, out_path)


if __name__ == "__main__":
    main()
