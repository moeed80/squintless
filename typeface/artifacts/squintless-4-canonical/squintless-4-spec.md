# Squintless Numeral 4 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `4` for the Pebble Time 2 watch face.

Codex must use the supplied SVG geometry as the source of truth. It must not redraw, reinterpret, replace, or substitute this numeral with a system font or seven-segment construction.

## Geometry

- SVG canvas: `1000 × 1000`
- ViewBox: `0 0 1000 1000`
- Visible bounds: `x = 85–945`, `y = 55–945`
- Visible width: `860`
- Visible height: `890`
- Left side bearing: `85`
- Right side bearing: `55`
- Top bearing: `55`
- Bottom bearing: `55`
- Right stem width: approximately `190`
- Crossbar thickness: approximately `175`
- Lower right extension: `235` pixels below the crossbar
- Main diagonal/left structure: broad continuous filled form
- Effective corner softening: approximately `55`

## Counter / open space

- Open triangular interior bounded approximately by:
  - top/right point: `670,300`
  - lower-left point: `445,535`
  - lower-right point: `670,535`
- The opening remains large enough to survive monochrome downscaling.
- The top remains open, preventing the glyph from resembling `9`.

## Optical corrections

- The right stem is deliberately heavy and continuous from cap height to baseline.
- The crossbar spans almost the full glyph width, making the numeral instantly recognizable.
- The left structure is broad rather than a fragile diagonal, preserving visual mass at oblique viewing angles.
- The top is open, while the lower right stem continues below the crossbar. This produces a strong, conventional `4` silhouette without using segmented construction.
- The glyph is slightly right-heavy, which is appropriate for `4`, but the broad crossbar prevents it from feeling narrow.

## Distinction risks

### Versus `9`

The `4` has:
- an open top;
- no enclosed upper bowl;
- a full-width crossbar;
- a lower right stem.

The future `9` must have one enclosed upper counter and a clearly separate lower extension.

### Versus `1`

The `4` uses a broad crossbar and a large open triangular structure. The canonical `1` has a single stem, shoulder, and base.

### Versus `7`

The `4` has a persistent right stem and crossbar. The future `7` should have a full top bar and one descending diagonal without a crossbar.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not close the open top.
- Do not thin the right stem, crossbar, or left structure.
- Do not crop inside the visible bounds.
- Pair spacing must be handled by layout code rather than modifying this SVG.

## Codex handoff

Use `squintless-4.svg` as the canonical source glyph.

Convert it to the Pebble-compatible resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
