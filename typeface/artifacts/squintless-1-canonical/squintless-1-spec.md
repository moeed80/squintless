# Squintless Numeral 1 — Canonical Glyph Specification

## Status

This SVG is the canonical Squintless numeral `1` for the Pebble Time 2 watch face.

Codex should use the supplied SVG geometry as the source of truth. It must not redraw, replace, reinterpret, or substitute the numeral with a system font or seven-segment construction.

## Geometry

- SVG canvas: `1000 × 1000`
- ViewBox: `0 0 1000 1000`
- Visible bounds: `x = 120–880`, `y = 55–945`
- Visible width: `760`
- Visible height: `890`
- Left side bearing: `120`
- Right side bearing: `120`
- Top bearing: `55`
- Bottom bearing: `55`
- Main stem width: approximately `200`
- Base thickness: `175`
- Base width: `760`
- Top shoulder reach: approximately `245` pixels to the left of the stem
- Outer corner treatment: approximately `55` pixels at the base; softened path transitions elsewhere
- Counters: none

## Optical corrections

- The glyph is deliberately much wider than an ordinary numeral `1`.
- A broad base prevents the numeral from disappearing at oblique angles.
- The left shoulder makes it immediately recognizable as `1`, rather than a plain vertical bar.
- The stem is optically centered over the base, while the shoulder adds controlled leftward weight.
- The pair `11` occupies substantial horizontal space and avoids the empty-screen effect typical of narrow digital ones.

## Distinction risks

### Versus `7`

The `1` has:

- a vertical primary stem;
- a wide horizontal base;
- a short left shoulder;
- no long descending diagonal.

The future `7` must use a full-width top and a clear descending diagonal so it cannot be mistaken for this glyph.

### Versus a lowercase `l` or vertical bar

The heavy base and pronounced shoulder make the silhouette unmistakably numeric.

## Rasterization guidance

- Preserve aspect ratio.
- Prefer nearest-neighbor or monochrome thresholding for final Pebble bitmap generation.
- Do not add antialiasing, gray pixels, outlines, shadows, or smoothing effects.
- Do not thin the stem or base.
- Do not crop inside the visible bounds.
- When pairing two digits, adjust inter-glyph spacing in layout code rather than modifying this canonical SVG.

## Codex handoff

Use `squintless-1.svg` as the canonical source glyph.

Convert it to the Pebble-compatible bitmap or resource format required by the project, preserving the exact silhouette and proportions. The SVG may be scaled uniformly, but its geometry must not be redrawn or reinterpreted.
