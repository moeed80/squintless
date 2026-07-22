# Squintless Typeface

This layer owns the reusable Squintless numeral design.

Each folder in `artifacts/` contains one production numeral. The SVG file is the source of truth, supported by preview PNGs and a glyph specification. The watchface must not redraw these numerals or replace them with a system font.

`fonts/red-hat-display/` contains the Red Hat Display font used for generated store typography and the Red Hat experimental edition. `fonts/russo-one/` contains the Russo One font used for the Russo experimental edition and the production date-glance month/day labels. Both fonts are third-party font software under the SIL Open Font License; Squintless source and custom numeral artwork remain MIT licensed.

Run this from the repository root after changing any canonical numeral:

```sh
python3 typeface/tools/generate_watchface_assets.py
```

The generator rasterizes the SVGs to hard monochrome Pebble bitmap resources and updates the generated watchface metrics, header files, and resource manifest.
