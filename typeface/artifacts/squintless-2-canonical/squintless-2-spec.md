# Squintless Numeral 2 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `2` for the Pebble Time 2 watch face.

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
- Top horizontal mass: approximately `635` pixels
- Upper-right vertical mass: approximately `200` pixels
- Diagonal transition: broad stepped sweep from upper-right to lower-left
- Base thickness: `175`
- Base width: `860`
- Effective corner softening: approximately `55` pixels at outer ends

## Optical corrections

- The top is deliberately broad and heavy so the glyph reads instantly at reduced contrast.
- The descending transition is not a fragile single diagonal; it is a wide, stepped geometric sweep that survives monochrome downscaling.
- The base spans the full glyph width, making the `2` visually stable and clearly different from `7`.
- The open left side in the upper half keeps the silhouette from resembling `8`.
- The lower-left entry into the base is intentionally blunt and architectural rather than calligraphic.

## Distinction risks

### Versus `7`

The `2` has:

- a broad upper bowl;
- a substantial descending transition;
- a full-width heavy base.

The future `7` must use a strong top bar and a single descending diagonal, without a lower bowl or full-width base.

### Versus `3`

The `2` has a decisive lower-left sweep into a full base. The future `3` should remain open on the left with two right-facing bowls.

### Versus `5`

The `2` begins with upper-right emphasis and descends leftward. The future `5` should begin with a strong top and left-side spine before opening into the lower bowl.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not thin the diagonal transition.
- Do not shorten or narrow the base.
- Do not crop inside the visible bounds.
- Handle pair spacing in layout code rather than modifying this SVG.

## Codex handoff

Use `squintless-2.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
