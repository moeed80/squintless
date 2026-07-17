# Squintless Typeface

This layer owns the reusable Squintless numeral design.

Each folder in `artifacts/` contains one production numeral. The SVG file is the source of truth, supported by preview PNGs and a glyph specification. The watchface must not redraw these numerals or replace them with a system font.

Run this from the repository root after changing any canonical numeral:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python typeface/tools/generate_watchface_assets.py
```

The generator rasterizes the SVGs to hard monochrome Pebble bitmap resources and updates the generated watchface metrics, header files, and resource manifest.
