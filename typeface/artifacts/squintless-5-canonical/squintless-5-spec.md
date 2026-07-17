# Squintless Numeral 5 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `5` for the Pebble Time 2 watch face.

Codex must use the supplied SVG geometry as the source of truth. It must not redraw, reinterpret, replace, or substitute this numeral with a system font or seven-segment construction.

## Geometry

- SVG canvas: `1000 × 1000`
- ViewBox: `0 0 1000 1000`
- Visible bounds: `x = 105–930`, `y = 55–945`
- Visible width: `825`
- Visible height: `890`
- Left side bearing: `105`
- Right side bearing: `70`
- Top bearing: `55`
- Bottom bearing: `55`
- Top bar thickness: `175`
- Upper left spine width: approximately `195`
- Middle horizontal mass: approximately `515`
- Lower bowl right spine: approximately `195`
- Bottom bar thickness: approximately `175`
- Effective outer corner softening: approximately `55`
- Counters: none; the lower bowl remains open on the left

## Optical corrections

- The top bar is deliberately broad and full-width, creating immediate recognition and a strong distinction from `6`.
- The upper-left spine is continuous and heavy, so the glyph reads as `5` rather than a reversed `2`.
- The lower bowl is large and slightly heavier than the upper structure, improving recognition at reduced contrast.
- The middle transition is broad and flat rather than thin or decorative.
- The left side of the lower bowl remains open, preventing the glyph from becoming visually enclosed like `6` or `8`.

## Distinction risks

### Versus `6`

The `5` has:
- a full-width top bar;
- a strong upper-left spine;
- an open lower-left bowl;
- no enclosed counter.

The future `6` must have a clearly enclosed lower counter and a distinct upper-left entry.

### Versus `2`

The `5` begins with a full-width top and descends through the left side. The canonical `2` begins with upper-right emphasis and sweeps diagonally into a full base.

### Versus `3`

The `5` has a strong upper-left structure and only one lower bowl. The canonical `3` has two right-facing bowls and no left spine.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not thin the upper-left spine or top bar.
- Do not close the lower-left opening.
- Do not crop inside the visible bounds.
- Handle pair spacing in layout code rather than modifying this SVG.

## Codex handoff

Use `squintless-5.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
