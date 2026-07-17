# Squintless Numeral 8 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `8` for the Pebble Time 2 watch face.

Codex must use the supplied SVG geometry as the source of truth. It must not redraw, reinterpret, replace, or substitute this numeral with a system font or seven-segment construction.

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
- Outer corner radius: `55`
- Inner corner radius: `38`
- Left and right wall thickness: `210`
- Top and bottom wall thickness: `95`
- Central bridge thickness: `110`

## Counters

### Upper counter
- Bounds: `x = 280–720`, `y = 150–445`
- Width: `440`
- Height: `295`
- Corner radius: `38`

### Lower counter
- Bounds: `x = 280–720`, `y = 555–850`
- Width: `440`
- Height: `295`
- Corner radius: `38`

The two counters are intentionally equal in size. This produces immediate recognition and avoids the visual ambiguity of an `8` whose lower bowl is excessively dominant.

## Optical corrections

- The glyph uses the full permitted width so it does not feel undersized beside `0` or `9`.
- Side walls are deliberately heavy to preserve silhouette at oblique viewing angles.
- The central bridge is thinner than the side walls but remains substantial enough to survive monochrome rasterization.
- The top and bottom walls are slightly thinner than the side walls to keep the counters open and prevent the form from becoming a black block.
- Corners are softened, but not so heavily rounded that visual mass is lost.

## Distinction risks

### Versus `0`

The `8` contains two clearly separated counters. The central bridge is wide enough to remain visible after downscaling, ensuring the glyph cannot collapse into a single-counter `0`.

### Versus `3`

The `8` is a fully enclosed form with continuous left and right walls. The future `3` must remain open on the left so its silhouette is unmistakably different.

### Versus `6` and `9`

The `8` is vertically symmetrical and contains two enclosed counters. The future `6` and `9` must use only one enclosed counter plus a clearly open or extended section.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing effects.
- Do not reduce the central bridge below its canonical proportion.
- Do not narrow the side walls.
- Do not crop inside the visible bounds.
- Pair spacing must be handled by layout code, not by modifying this SVG.

## Codex handoff

Use `squintless-8.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
