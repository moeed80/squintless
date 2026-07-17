# Squintless Watchface

This is the Pebble Time 2 watchface project. It renders time and battery state using bitmap assets generated from the canonical typeface layer.

Build:

```sh
pebble build
```

Run on the Pebble Time 2 emulator:

```sh
pebble install --emulator emery
```

Generate validation previews from the bitmap resources:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python tools/render_previews.py
```

The numeral assets are generated. Do not edit `resources/images/` or `src/c/generated/` by hand; update `../typeface/artifacts/` and rerun the generator instead.
