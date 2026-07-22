# Squintless Russo Edition

Pebble Time 2 watchface variant using official Russo One numerals from Google Fonts.

This build exists for readability comparison against:

- `watchface/`: Squintless SVG Edition
- `watchface-redhat/`: Squintless Red Hat Edition

The layout, battery indicator, update logic, and Emery target match the other editions. The main numeral source changes to Russo One.

This project is also the source for the Squintless 1.1 App Store PBW. The release builder applies the production `Squintless` name, UUID, icon, and version metadata without changing this variant's local install identity.

Tapping or shaking the watch temporarily replaces the time with a large Russo One month/day date for three seconds, then returns to the default face.

## Build

```sh
pebble build
```

The requested build artifact is:

```text
build/watchface-russo.pbw
```
