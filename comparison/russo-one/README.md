# Russo One Comparison

This folder contains the controlled Squintless Russo Edition experiment.

## Editions Compared

- SVG Edition: `watchface/`
- Red Hat Display Edition: `watchface-redhat/`
- Russo One Edition: `watchface-russo/`

## Font Source

Russo One was obtained from the official Google Fonts repository:

- Upstream source: `https://github.com/google/fonts/tree/main/ofl/russoone`
- Font file: `RussoOne-Regular.ttf`
- Local source note: `../../typeface/fonts/russo-one/SOURCE.md`

## Battery Geometry

The previous outlined battery bar used a 7 px outer height with a 1 px border, leaving a 5 px white/fill interior.

Pebble's 1-bit display cannot make a robust border thinner than 1 px. To increase the visible interior by approximately 2 px, the updated geometry uses:

- Outer width: 190 px
- Outer horizontal inset: 5 px
- Outer height: 9 px
- Border: 1 px
- Interior height: 7 px

The bar centerline and numeral regions remain unchanged.

## Visual Review

The Russo One numerals remain bold and readable without altering glyph outlines. Wide pairs such as `08`, `88`, `90`, and `99` fit without clipping. `10`, `11`, `18`, `20`, and `22` maintain at least 3 px of top display padding in the 200 x 228 preview renders.

The updated battery bar has a clearer empty interior while staying subordinate to the numerals.
