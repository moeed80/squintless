# Squintless Numeral 6 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `6` for the Pebble Time 2 watch face.

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
- Main left structure: broad continuous entry from cap height into the lower bowl
- Lower bowl outer width: approximately `860`
- Effective outer corner softening: approximately `55`
- Lower counter corner radius: approximately `45`

## Counter

- Bounds: `x = 220–775`, `y = 545–795`
- Width: `555`
- Height: `250`
- Corner radius: approximately `45`

The lower counter is intentionally large and horizontally broad so it remains open after monochrome rasterization.

## Optical corrections

- The upper-right region remains clearly open, preventing the glyph from collapsing into an `8`.
- The upper-left entry is broad and heavy, so the numeral does not resemble a `5`.
- The lower bowl carries most of the visual mass, producing a familiar and quickly recognized `6` silhouette.
- The lower counter is wider than it is tall, which improves recognition on the compact Pebble display.
- The upper curve transitions into the bowl as one continuous shape rather than separate segments.

## Distinction risks

### Versus `5`

The `6` contains one fully enclosed lower counter and a curved upper-left entry. The canonical `5` has no enclosed counter, a full-width top bar, and an open lower-left bowl.

### Versus `8`

The `6` has only one enclosed counter and a clearly open upper-right region. The canonical `8` has two enclosed counters separated by a central bridge.

### Versus `0`

The `6` is strongly asymmetrical, with an open upper-right region and a weighted lower bowl. The canonical `0` is vertically symmetrical and contains one tall uninterrupted counter.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not close the upper-right opening.
- Do not shrink the lower counter.
- Do not thin the upper-left entry or lower bowl walls.
- Do not crop inside the visible bounds.
- Pair spacing must be handled by layout code rather than modifying this SVG.

## Codex handoff

Use `squintless-6.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
