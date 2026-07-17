# Squintless Numeral 0 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `0` for the Pebble Time 2 watch face.

Codex must use the supplied SVG geometry as the source of truth. It must not redraw, reinterpret, replace, or substitute the numeral with a system font, seven-segment construction, or alternate zero.

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
- Top and bottom wall thickness: `135`

## Counter

- Bounds: `x = 280–720`, `y = 190–810`
- Width: `440`
- Height: `620`
- Corner radius: `38`

The counter is deliberately tall and open so the glyph remains readable at reduced contrast and oblique viewing angles.

## Optical corrections

- The glyph uses the full regular width to maintain equal visual authority beside `8` and `9`.
- Side walls are heavier than the top and bottom walls, which helps the silhouette stay stable when the reflective display loses contrast at an angle.
- The outer shape is squarer than a conventional oval zero. This preserves black visual mass and matches the architectural Squintless design language.
- The internal opening is tall enough that the glyph does not become a black block after monochrome rasterization.
- Top and bottom walls remain thick enough to distinguish the glyph from two separated vertical bars.

## Distinction risks

### Versus `8`

The `0` contains one uninterrupted counter extending through most of the glyph height. The canonical `8` contains two distinct counters separated by a central bridge.

### Versus `6` and `9`

The `0` is vertically symmetrical and has no open section, tail, or asymmetric bowl. Future `6` and `9` glyphs must use one enclosed counter plus a clearly differentiated open or extended region.

### Versus the letter `O`

The near-rectangular geometry, heavy side walls, and proportions are intentionally more numeric and display-oriented than a conventional typographic capital `O`.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor scaling or monochrome thresholding for final Pebble resources.
- Do not add antialiasing, gray pixels, shadows, outlines, or smoothing.
- Do not reduce the side-wall thickness.
- Do not shrink the counter.
- Do not crop inside the visible bounds.
- Handle spacing in layout code rather than editing this SVG.

## Codex handoff

Use `squintless-0.svg` as the canonical source glyph.

Convert it to the Pebble-compatible bitmap or resource format required by the project while preserving the exact silhouette and proportions. Uniform scaling is permitted. Redrawing or reinterpretation is not.
