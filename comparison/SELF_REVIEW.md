# Squintless SVG Edition vs Font Edition

This review compares the current canonical SVG implementation against the experimental Red Hat Display Black implementation. Both use the same Pebble Time 2 layout, battery bar, margins, update behavior, and bitmap rendering path.

## Sources

- SVG Edition: `typeface/artifacts/squintless-*-canonical/*.svg`
- Font Edition: `typeface/font-edition/fonts/RedHatDisplay-wght.ttf`, sourced from `https://github.com/google/fonts/tree/main/ofl/redhatdisplay`
- Font instance: Red Hat Display, `wght=900`

## Validation Set

Generated screenshots cover:

- `08:36`
- `11:11`
- `12:34`
- `20:58`
- `01:05`
- `06:49`
- `09:06`
- `18:18`
- `22:22`

Pair spacing was checked for:

- `00`, `08`, `10`, `11`, `18`, `20`, `22`, `36`, `47`, `58`, `69`, `77`, `88`, `90`, `99`

## SVG Edition

The SVG Edition has the stronger low-vision silhouette. It uses the Pebble Time 2 width more consistently, especially in narrow pairs such as `11`, and the numerals keep a heavy, unified presence when reduced or viewed quickly. The edges are crisp because the watchface uses 1-bit bitmap resources generated from the canonical SVG shapes.

The tradeoff is that some digits are less conventional than a familiar typeface. Recognition of `2`, `3`, `5`, `6`, and `9` depends on learning the Squintless visual language, though the forms remain distinct in the validation set.

## Font Edition

The Font Edition benefits from familiar Red Hat Display numeral shapes. Mixed pairs such as `12`, `36`, `58`, `69`, and `90` read quickly because the digits align with ordinary typographic expectations. The result looks more like a professional typeface and less like a custom instrument display.

The main weakness is perceived size. Because the actual Red Hat Display outlines are preserved without condensing or stretching, narrow glyphs and pairs cannot fill the available width. `11` is the clearest example: it is optically clean, but substantially smaller on the screen than the SVG Edition. This makes the Font Edition feel lighter and less assertive at reduced scale, even though the font size is pushed to the largest non-clipping size.

## Battery Bar

Both editions correctly render the same full-width battery track:

- Charged section: solid black
- Remaining section: light gray
- Minimum visible fill preserved for low nonzero battery values

## Verdict

Neither edition is strictly superior in every condition.

For the stated Squintless goal of maximum Pebble Time 2 glance readability, the SVG Edition currently has the edge. Its numerals occupy more of the screen, maintain stronger visual weight, and make better use of the rectangular display. It is more legible when contrast drops or the image is reduced.

The Font Edition is still valuable. It improves conventional recognition speed and demonstrates that several Red Hat Display proportions, especially in `2`, `3`, `5`, `6`, and `9`, could inform future Squintless revisions.

The next Squintless numeral pass should combine the SVG Edition's screen-filling mass, wide `1`, and consistent row weight with the Font Edition's familiar digit cues and calmer mixed-pair spacing.
