# Squintless Russo Edition

Rectangular Pebble watchface variant using official Russo One numerals from Google Fonts.

This build exists for readability comparison against:

- `watchface/`: Squintless SVG Edition
- `watchface-redhat/`: Squintless Red Hat Edition

The layout, battery indicator, and update logic match the other editions. The main numeral source changes to Russo One.

This project is also the source for the Squintless 1.2 App Store PBW. The release builder applies the production `Squintless` name, UUID, icon, platform targets, and version metadata without changing this variant's local install identity.

Version 1.2 includes platform-specific bitmap resources for `200 x 228` Emery and `144 x 168` rectangular Pebble watches. Pebble Time Round / `chalk` is intentionally excluded.

Tapping or shaking the watch temporarily replaces the time with a large Russo One month/day date for three seconds, then returns to the default face.

## Build

```sh
pebble build
```

The requested build artifact is:

```text
build/watchface-russo.pbw
```
