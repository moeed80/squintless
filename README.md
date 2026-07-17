# Squintless

Designed for your aging eyes, not your ego.

![Squintless feature graphic](store/feature/squintless-feature-1600x900.png)

Squintless is an accessibility-first watch face for Pebble Time 2. It exists for one job: let you tell the time instantly.

No date. No weather. No step count. No seconds. No icons. No decorative complications.

Every pixel is there to improve readability.

## Philosophy

Most watch faces try to prove how much information they can fit on a tiny screen. Squintless goes the other way.

The top half is hours. The bottom half is minutes. The middle is a quiet battery indicator. The result is a watch face you can read with a quick glance, even when your near vision is not cooperating.

Squintless is built for people over 40, people whose close-up vision has changed, and anyone who values function over decoration.

It is not a retro watch face. It is not a minimalist art project. It is a purpose-built accessibility product.

## Screenshots

![Straight-on hero shot](store/screenshots/01-straight-on-hero.png)
![Angled wrist readability shot](store/screenshots/02-angled-wrist-readability.png)
![Large time close-up](store/screenshots/03-large-time-close-up.png)
![Battery almost empty](store/screenshots/04-battery-almost-empty.png)
![Pair spacing example](store/screenshots/05-pair-spacing.png)

## Layout

Squintless uses the full 200 x 228 Pebble Time 2 display:

- Hours fill the upper half.
- Minutes fill the lower half.
- The battery indicator sits between them.

The layout is deliberately stable. There are no animations, secondary modes, or information layers competing with the time.

## Battery Indicator

The center line always spans the same width.

- Black shows charge remaining.
- Light gray shows capacity already used.
- Very low nonzero battery still gets a small visible black segment.

It reads as a drain line without pulling attention away from the numerals.

## Typography

The numerals are custom Squintless glyphs. They are not a system font and they are not drawn procedurally by the watch face.

The reusable typeface layer owns the SVG source artwork for every digit. The build tools convert those SVGs into hard monochrome Pebble bitmap resources, including pair-specific bitmaps for optical spacing.

That separation keeps the product clean:

- `typeface/` defines how the numerals look.
- `watchface/` renders time and battery state.

Future numeral changes should happen in the typeface layer first.

## Compatibility

Squintless 1.0 is built specifically for Pebble Time 2.

- Platform: `emery`
- Resolution: `200 x 228`
- Display: rectangular

Version 1.0 does not compromise the layout for older 144 x 168 Pebble watches.

## Installation

Build the Pebble package:

```sh
cd watchface
pebble build
```

The generated package is:

```text
watchface/build/watchface.pbw
```

Install on the Pebble Time 2 emulator:

```sh
cd watchface
pebble install --emulator emery
```

Install on a physical watch through the Pebble mobile app Developer Connection:

```sh
cd watchface
pebble install --phone <PHONE_IP> build/watchface.pbw
```

## Development

Install the current supported Pebble tooling:

```sh
brew install python node uv python@3.13 libpng cairo
uv tool install pebble-tool --python 3.13
uv pip install --python /Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python cairosvg
pebble sdk install latest
```

Regenerate watchface assets after changing numeral SVGs:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python typeface/tools/generate_watchface_assets.py
```

Generate store artwork and the Pebble menu icon:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python tools/generate_store_assets.py
```

Generate developer previews:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python watchface/tools/render_previews.py
```

App Store metadata lives in `store/metadata.md` and `store/metadata.json`.

## Project Structure

```text
Squintless/
  typeface/
    artifacts/
    tools/

  watchface/
    package.json
    resources/
    src/c/
    tools/

  store/
    feature/
    icon/
    screenshots/
    metadata.md
    metadata.json
```

## Release Checklist

- Product name is `Squintless`.
- App Store copy is in `store/metadata.md`.
- App icon and feature graphic are in `store/`.
- Pebble menu icon is bundled as a watchface resource.
- The watchface targets only `emery`.
- The build output is `watchface/build/watchface.pbw`.
