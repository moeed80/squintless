# Squintless Watchface

This is the production Pebble Time 2 watchface project for Squintless.

The watchface renders only:

- Hours
- Battery drain line
- Minutes

All numeral artwork is generated from `../typeface/artifacts/`. Do not edit `resources/images/` or `src/c/generated/` by hand.

## Build

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
