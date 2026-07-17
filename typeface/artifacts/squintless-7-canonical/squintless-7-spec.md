# Squintless Numeral 7 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `7` for the Pebble Time 2 watch face.

Codex must use the supplied SVG geometry as the source of truth. It must not redraw, reinterpret, replace, or substitute the numeral with a system font or seven-segment construction.

## Geometry

- SVG canvas: `1000 × 1000`
- ViewBox: `0 0 1000 1000`
- Visible bounds: `x = 70–930`, `y = 55–945`
- Visible width: `860`
- Visible height: `890`
- Left side bearing: `70`
- Right side bearing: `70`
- Top bearing: `55`
- Bottom bearing: `55`
- Top bar thickness: `175`
- Top bar width: `860`
- Descending diagonal effective thickness: approximately `185–205`
- Lower terminal width: approximately `205`
- Effective outer corner softening: approximately `55`
- Counters: none

## Optical corrections

- The full-width top bar makes the numeral unmistakably `7` at a glance.
- The descending stroke is deliberately broad, avoiding a fragile diagonal or single-pixel tip after rasterization.
- The lower terminal is blunt and substantial rather than pointed.
- There is no lower base or crossbar, preserving a strong distinction from `2` and `4`.
- The diagonal starts well inside the right side of the top bar, creating a familiar and stable silhouette.
- The glyph uses the full regular width so a pair such as `77` does not feel visually weak.

## Distinction risks

### Versus `1`

The `7` has:
- a full-width top bar;
- a broad descending diagonal;
- no vertical stem;
- no base.

The canonical `1` has a vertical stem, left shoulder, and wide base.

### Versus `2`

The `7` has no lower sweep and no full-width base. The canonical `2` includes a broad descending transition that resolves into a heavy lower base.

### Versus `4`

The `7` has no crossbar or persistent right stem. The canonical `4` includes both a strong crossbar and a vertical right structure.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not thin the diagonal.
- Do not sharpen the lower terminal into a fragile point.
- Do not shorten or narrow the top bar.
- Do not crop inside the visible bounds.
- Handle pair spacing in layout code rather than modifying this SVG.

## Codex handoff

Use `squintless-7.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
