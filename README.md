# Squintless

Squintless is split into two separate systems:

```text
Squintless/
  typeface/
    artifacts/
      squintless-0-canonical/
      ...
      squintless-9-canonical/
    font-edition/
      fonts/
      tools/
    tools/
      generate_watchface_assets.py

  watchface/
    package.json
    src/c/
    resources/images/
    tools/

  watchface-font/
    package.json
    src/c/
    resources/images/
    tools/

  comparison/
    screenshots/
```

The typeface owns numeral design. The watchface renders time and battery state.

## Editions

This branch keeps two complete implementations side by side:

- `watchface/`: Squintless SVG Edition, generated from the canonical Squintless SVG numerals.
- `watchface-font/`: Squintless Font Edition, generated from Red Hat Display at `wght=900`.

Both projects use the same Pebble Time 2 layout, battery bar, colors, margins, update cadence, and bitmap rendering architecture. Only the numeral bitmap source differs.

## Typeface

`typeface/artifacts/` contains the canonical Squintless numerals. Each digit folder includes the SVG source and supporting specification/preview files. The SVG is the source of truth; the watchface does not redraw, reinterpret, or substitute the numerals.

The generator converts those SVGs into Pebble bitmap resources:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python typeface/tools/generate_watchface_assets.py
```

It writes:

- `watchface/resources/images/singles/*.png`
- `watchface/resources/images/pairs/*.png`
- `watchface/src/c/generated/squintless_typeface_assets.h`
- `watchface/src/c/generated/squintless_typeface_metrics.json`
- the `watchface/package.json` resource manifest entries

Future numeral design changes should happen in `typeface/artifacts/`, then this generator should be rerun.

`typeface/font-edition/` contains the experimental Red Hat Display Black source and generator. The font was obtained from the official Google Fonts repository:

- Repository: `https://github.com/google/fonts`
- Path: `ofl/redhatdisplay/RedHatDisplay[wght].ttf`
- Local file: `typeface/font-edition/fonts/RedHatDisplay-wght.ttf`
- Instance: `wght=900`, the Black weight

Generate the Font Edition assets with:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python typeface/font-edition/tools/generate_watchface_font_assets.py
```

## Watchface

Both Pebble projects target Pebble Time 2:

- Platform: `emery`
- Resolution: `200 x 228`
- Display: rectangular

Each watchface uses generated bitmap resources only. It loads the current hour and minute bitmap assets, draws them at native size, and never stretches or distorts them.

The battery bar always spans the full available width. The charged part is black; the remaining part is `GColorLightGray`, giving a visible drain track while preserving the existing thickness and low-battery minimum-fill behavior.

## Build

Install the current supported Pebble tooling:

```sh
brew install python node uv python@3.13 libpng cairo
uv tool install pebble-tool --python 3.13
uv pip install --python /Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python cairosvg
pebble sdk install latest
```

Generate and build the SVG Edition:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python typeface/tools/generate_watchface_assets.py
cd watchface
pebble build
```

The built package is:

```text
watchface/build/watchface.pbw
```

Generate and build the Font Edition:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python typeface/font-edition/tools/generate_watchface_font_assets.py
cd watchface-font
pebble build
```

The built package is:

```text
watchface-font/build/watchface-font.pbw
```

## Emulator

SVG Edition:

```sh
cd watchface
pebble install --emulator emery
```

Font Edition:

```sh
cd watchface-font
pebble install --emulator emery
```

Physical install:

```sh
cd watchface
pebble install --phone <PHONE_IP> build/watchface.pbw
```

## Validation Previews

Generate the validation screenshots from the same bitmap resources used by the watchface:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python watchface/tools/render_previews.py
```

Generate Font Edition screenshots:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python watchface-font/tools/render_previews.py
```

Generate side-by-side comparisons:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python tools/render_edition_comparison.py
```

Screenshots are written to `watchface/screenshots/` for:

- `08:36`
- `11:11`
- `12:34`
- `20:58`
- `01:05`
- `06:49`
- `09:06`
- `18:18`
- `22:22`

Font Edition screenshots are written to `watchface-font/screenshots/`. Side-by-side comparisons are written to `comparison/screenshots/`.

The experimental visual critique is documented in `comparison/SELF_REVIEW.md`.

## Validation Notes

Completed locally:

- Moved canonical numeral artifacts into `typeface/artifacts/`.
- Moved the Pebble app into `watchface/`.
- Removed the procedural C numeral renderer.
- Generated native-size bitmap resources from the canonical SVG assets.
- Generated pair-specific bitmap resources for `00` through `99`.
- Validated required spacing pairs: `11`, `10`, `18`, `08`, `88`, `20`, `22`, `36`, `49`, `58`, `69`, `90`.
- Built successfully for `emery` with SDK `4.17`.
- Added the Red Hat Display Black Font Edition as a separate project without changing the canonical SVG implementation.

Known limitation:

- The SDK linker still emits its existing RWX LOAD segment warning. The Squintless C source builds cleanly.
