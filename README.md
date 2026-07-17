# Squintless

Squintless is an accessibility-first Pebble watchface for Pebble Time 2. It shows only:

- Hours in the upper half
- A proportional battery line in the central gap
- Minutes in the lower half

It intentionally does not show date, weather, steps, battery percent, icons, seconds, Bluetooth status, AM/PM, menus, or button interactions.

## Target

- Watch: Pebble Time 2
- Platform: `emery`
- Display: 200 x 228 rectangular
- Version 1 target platforms: `emery` only

This version does not compromise the layout for older 144 x 168 Pebbles.

## Readability Design

The numerals are drawn directly with Pebble graphics primitives instead of using a system font. The default renderer is `SQUINTLESS_STYLE_SOLID`: each digit is a continuous filled geometric glyph with white counters/openings carved back out. The original segmented renderer is retained behind `SQUINTLESS_STYLE_SEGMENTED` for comparison.

The design favors:

- maximum size on the 200 x 228 display
- high black-white contrast
- heavy continuous silhouettes
- large rectangular internal openings
- a visibly wide `1`
- differentiated `0`, `6`, `8`, and `9`
- no seven-segment gaps
- no antialiasing, gray edges, iconography, or fine detail

The face uses one `Window` and one custom `Layer`. The update procedure draws background, hours, battery line, and minutes in that order.

## Build

Install the current supported Pebble tooling on macOS:

```sh
brew install python node uv python@3.13 libpng
uv tool install pebble-tool --python 3.13
pebble sdk install latest
```

Build:

```sh
pebble build
```

The generated package is:

```sh
build/Squintless.pbw
```

## Emulator

Install and run on the Pebble Time 2 emulator:

```sh
pebble install --emulator emery
```

Useful validation commands:

```sh
pebble emu-time-format --format 24h
pebble emu-set-time 08:36:00
pebble emu-battery --percent 75
pebble screenshot screenshots/emery-08-36-battery-75.png --no-open
```

```sh
pebble emu-set-time 11:11:00
pebble emu-battery --percent 50
pebble screenshot screenshots/emery-11-11-battery-50.png --no-open
```

```sh
pebble emu-time-format --format 12h
pebble emu-set-time 13:05:00
pebble emu-battery --percent 15
pebble screenshot screenshots/emery-1-05-12h-battery-15.png --no-open
```

If the emulator continues to report 24-hour style to `clock_is_24h_style()`, use the preview renderer for the exact 12-hour visual validation:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python tools/render_previews.py
```

## Physical Watch Install

Enable Developer Connection in the Pebble mobile app, note the phone IP address, then run:

```sh
pebble install --phone <PHONE_IP> build/Squintless.pbw
```

## Cloud IDE Import

The current Rebble cloud flow is at:

```text
https://cloud.repebble.com
```

Import steps:

1. Launch the cloud environment.
2. In the terminal, run:

```sh
code /workspaces/codespaces-pebble
```

3. Upload this project folder, excluding `build` if present.
4. Click the Pebble icon in the left sidebar.
5. Choose `Open Project` and select `Squintless`.
6. Build or run on the `emery` emulator from the Pebble sidebar.

## Layout Tuning

Most layout values are centralized near the top of `src/c/squintless.c`:

- `outer_margin`
- `central_gap_h`
- `battery_line_h`
- `battery_line_inset`
- `default_digit_spacing_units`
- `digit_corner_radius`
- `low_battery_min_w`
- `DIGIT_UNITS_W`
- `DIGIT_UNITS_H`

The digit geometry is in `prv_draw_solid_digit` and `prv_draw_segmented_digit`.

## Refining Numerals

To replace or refine the solid numeral design, edit `prv_draw_solid_digit` in `src/c/squintless.c`. Each digit uses a 13 x 15 unit coordinate grid, except `1`, which uses an 11-unit width for better spacing. Keep strokes joined and thick, then run:

```sh
pebble build
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python tools/render_previews.py
```

To build with the older segmented style temporarily, change:

```c
#define SQUINTLESS_NUMERAL_STYLE SQUINTLESS_STYLE_SOLID
```

to:

```c
#define SQUINTLESS_NUMERAL_STYLE SQUINTLESS_STYLE_SEGMENTED
```

The preview renderer mirrors the C layout and writes `solid-*`, `segmented-*`, and `compare-*` images for:

- `08:36`
- `11:11`
- `12:34`
- `20:58`
- `1:05` in 12-hour mode
- `6:49` in 12-hour mode
- `9:06` in 12-hour mode

## Validation Notes

Completed locally:

- Installed `pebble-tool` 5.0.39 with SDK 4.17.
- Confirmed `emery` is supported by the installed SDK.
- Built `build/Squintless.pbw` for `emery`.
- Ran the `emery` emulator and installed the watchface.
- Captured live emulator screenshots for 08:36 at 75% and 11:11 at 50%.
- Generated solid, segmented, and side-by-side comparison previews for the revised numeral set.

Known limitations:

- The local `emery` emulator accepted `pebble emu-time-format --format 12h`, but `clock_is_24h_style()` still behaved as 24-hour during the live screenshot session. The 12-hour rendering path is implemented in C and validated with `tools/render_previews.py`; it still needs confirmation on the physical Pebble Time 2.
- The SDK linker emitted an RWX LOAD segment warning from the toolchain while producing a successful build. No C compiler warnings remained in Squintless.
- Version 1 is deliberately `emery` only.
