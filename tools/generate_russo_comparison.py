#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "comparison" / "russo-one"
ROWS_DIR = OUT_DIR / "rows"

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

EDITIONS = [
    ("SVG Edition", ROOT / "watchface" / "previews"),
    ("Red Hat Display Edition", ROOT / "watchface-redhat" / "previews"),
    ("Russo One Edition", ROOT / "watchface-russo" / "previews"),
]


def load_preview(directory: Path, slug: str, battery: int) -> Image.Image:
    return Image.open(directory / f"squintless-{slug}-battery-{battery}.png").convert("L")


def label_font(size: int) -> ImageFont.ImageFont:
    red_hat = ROOT / "typeface" / "fonts" / "red-hat-display" / "RedHatDisplay-wght.ttf"
    if red_hat.exists():
        font = ImageFont.truetype(str(red_hat), size)
        font.set_variation_by_axes([700])
        return font
    return ImageFont.load_default()


def centered_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont) -> None:
    x0, y0, x1, y1 = box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        (x0 + (x1 - x0 - text_w) // 2, y0 + (y1 - y0 - text_h) // 2 - bbox[1]),
        text,
        fill=0,
        font=font,
    )


def make_row(slug: str, battery: int) -> Image.Image:
    cell_w = 200
    cell_h = 228
    gap = 16
    label_h = 28
    title_h = 26
    width = cell_w * len(EDITIONS) + gap * (len(EDITIONS) - 1)
    height = title_h + label_h + cell_h
    out = Image.new("L", (width, height), 255)
    draw = ImageDraw.Draw(out)
    label = label_font(12)
    title = label_font(18)
    centered_text(draw, (0, 0, width, title_h), slug.replace("-", ":"), title)
    for index, (edition, directory) in enumerate(EDITIONS):
        x = index * (cell_w + gap)
        centered_text(draw, (x, title_h, x + cell_w, title_h + label_h), edition, label)
        out.paste(load_preview(directory, slug, battery), (x, title_h + label_h))
    return out


def main() -> None:
    ROWS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for _hour, _minute, battery, slug in STATES:
        row = make_row(slug, battery)
        row.save(ROWS_DIR / f"squintless-three-way-{slug}-battery-{battery}.png")
        rows.append(row)

    gap = 20
    sheet_w = max(row.width for row in rows)
    sheet_h = sum(row.height for row in rows) + gap * (len(rows) - 1)
    sheet = Image.new("L", (sheet_w, sheet_h), 255)
    y = 0
    for row in rows:
        sheet.paste(row, ((sheet_w - row.width) // 2, y))
        y += row.height + gap
    sheet.save(OUT_DIR / "squintless-russo-three-way-contact-sheet.png")


if __name__ == "__main__":
    main()
