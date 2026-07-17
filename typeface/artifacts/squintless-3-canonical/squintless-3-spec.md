# Squintless Numeral 3 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `3` for the Pebble Time 2 watch face.

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
- Top bar thickness: approximately `100`
- Middle bridge thickness: approximately `165`
- Bottom bar thickness: approximately `175`
- Right spine thickness: approximately `195`
- Effective outer corner softening: approximately `55`
- Counters: none; both bowls remain open on the left

## Optical corrections

- The lower bowl is slightly larger and heavier than the upper bowl. This matches common numeral recognition patterns and helps the glyph remain stable at a glance.
- The right spine is continuous from top to bottom, giving the numeral one strong silhouette rather than separated display segments.
- The left side remains clearly open in both bowls, preventing confusion with `8`.
- The middle bridge is substantial enough to survive monochrome rasterization but does not close the left side.
- The glyph is slightly right-heavy by design, as expected for a geometric `3`, while the broad top and base prevent it from feeling narrow.

## Distinction risks

### Versus `8`

The `3` has two open left-facing cavities and no enclosed counters. The canonical `8` is fully enclosed and contains two separate counters.

### Versus `2`

The `3` has two right-facing bowls and no diagonal sweep into a full-width base. The canonical `2` uses a decisive descending transition and broad lower base.

### Versus `9`

The `3` has no enclosed upper bowl and no descending stem. The future `9` must contain one enclosed counter and a distinct lower extension.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not close either left-side opening.
- Do not narrow the middle bridge or right spine.
- Do not crop inside the visible bounds.
- Handle pair spacing in layout code rather than modifying this SVG.

## Codex handoff

Use `squintless-3.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
