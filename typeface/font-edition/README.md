# Squintless Font Edition Typeface

This experimental typeface layer uses Red Hat Display at the Black weight as a comparison against the canonical Squintless SVG numerals.

Source:

- Repository: `https://github.com/google/fonts`
- Path: `ofl/redhatdisplay/RedHatDisplay[wght].ttf`
- Local file: `fonts/RedHatDisplay-wght.ttf`
- Instance: `wght=900`, the Black weight
- License: SIL Open Font License, included as `fonts/OFL.txt`

Generate Font Edition watchface assets from the repository root:

```sh
/Users/moeedahmad/.local/share/uv/tools/pebble-tool/bin/python typeface/font-edition/tools/generate_watchface_font_assets.py
```

Do not edit generated files under `watchface-font/resources/` or `watchface-font/src/c/generated/` by hand.
