# Squintless Font Edition Watchface

This is the experimental Red Hat Display Black edition of the Squintless Pebble Time 2 watchface.

It keeps the SVG Edition layout, battery bar, colors, update behavior, and rendering architecture. Only the numeral bitmap source changes.

Build:

```sh
pebble build
```

Run on the Pebble Time 2 emulator:

```sh
pebble install --emulator emery
```

Generate validation previews:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python tools/render_previews.py
```

The numeral assets are generated from `../typeface/font-edition/fonts/RedHatDisplay-wght.ttf` at `wght=900`. Do not edit `resources/images/` or `src/c/generated/` by hand.
