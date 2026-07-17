# Squintless Numeral 9 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `9` for the Pebble Time 2 watch face.

Codex must use the supplied SVG geometry as the source of truth. It must not redraw, reinterpret, replace, or substitute this numeral with a system font or seven-segment construction.

## Geometry

- SVG canvas: `1000 × 1000`
- ViewBox: `0 0 1000 1000`
- Visible bounds: `x = 70–930`, `y = 55–930`
- Visible width: `860`
- Visible height: `875`
- Left side bearing: `70`
- Right side bearing: `70`
- Top bearing: `55`
- Bottom bearing: `70`
- Upper bowl outer width: approximately `860`
- Right stem: heavy continuous structure through the full upper and middle sections
- Lower extension: broad descending continuation with an open lower-left region
- Effective outer corner softening: approximately `55`
- Upper counter corner radius: approximately `45`

## Counter

- Bounds: `x = 225–775`, `y = 205–455`
- Width: `550`
- Height: `250`
- Corner radius: approximately `45`

The upper counter is intentionally large and horizontally broad so it remains open after monochrome rasterization.

## Optical corrections

- The upper bowl carries most of the visual mass, producing immediate recognition as `9`.
- The right stem remains continuous and heavy, avoiding a segmented appearance.
- The lower-left region stays clearly open, preventing the glyph from becoming an `8` or `0`.
- The lower extension is broad and blunt rather than thin or pointed.
- The bottom ends slightly above the shared baseline to keep the glyph visually balanced and distinguish it from `4`.
- The upper counter is wider than it is tall, matching the compact display proportions and improving recognition at small sizes.

## Distinction risks

### Versus `0`

The `9` has one upper counter, a strongly asymmetric body, and an open lower-left region. The canonical `0` is vertically symmetrical and contains one tall uninterrupted counter.

### Versus `8`

The `9` contains only one enclosed counter and has a clear lower extension. The canonical `8` contains two enclosed counters separated by a central bridge.

### Versus `4`

The `9` has one enclosed upper bowl and no full-width crossbar. The canonical `4` has an open top, a broad crossbar, and a lower right stem.

### Versus `6`

The `9` is the top-weighted counterpart to `6`: one upper counter and an open lower-left region. The canonical `6` has one lower counter and an open upper-right region.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not close the lower-left opening.
- Do not shrink the upper counter.
- Do not thin the right stem or lower extension.
- Do not crop inside the visible bounds.
- Pair spacing must be handled by layout code rather than modifying this SVG.

## Codex handoff

Use `squintless-9.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
