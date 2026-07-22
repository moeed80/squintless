# Squintless Watchface

This is the production Pebble Time 2 watchface project for Squintless.

The default watchface renders only:

- Hours
- Outlined battery progress indicator
- Minutes

Pressing the middle button temporarily replaces the time with a large Russo One month/day date for three seconds, then returns to the default face.

All numeral artwork is generated from `../typeface/artifacts/`. Do not edit `resources/images/` or `src/c/generated/` by hand.

Date-glance month and day artwork is generated from the official Russo One font in `../typeface/fonts/russo-one/`.

## Build

Regenerate date-glance month and day assets:

```sh
python3 tools/generate_date_glance_assets.py
```

```sh
pebble build
```

The built package is:

```text
build/watchface.pbw
```

## Emulator

```sh
pebble install --emulator emery
```

## Resources

The package includes:

- `IMAGE_MENU_ICON`: Pebble menu icon
- `IMAGE_SINGLE_0` through `IMAGE_SINGLE_9`: single-digit fallback resources
- `IMAGE_PAIR_00` through `IMAGE_PAIR_99`: pair-specific time resources with optical spacing

The product metadata and promotional artwork live in `../store/`.
