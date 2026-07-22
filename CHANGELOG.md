# Changelog

All notable changes to Squintless will be documented here.

## Unreleased

## 1.2.0 - 2026-07-22

- Added rectangular Pebble compatibility for 144 x 168 watches.
- Added platform-specific `~144w~168h` Russo One numeral and date-glance bitmap resources.
- Kept the Pebble Time 2 `emery` numeral assets pixel-identical to the 1.1 release.
- Added a compact 144 x 168 layout profile for the battery bar and date separator.
- Added an `aplite` resource-saving path that composes time from single digit bitmaps to stay under the 128 KB resource limit.
- Updated the release builder to emit a multi-platform rectangular App Store package.
- Added 144 x 168 developer previews for time, date glance, and battery validation.

## 1.1.0 - 2026-07-22

- Prepared the App Store 1.1 package from the real-device-tested Russo One readability treatment.
- Added a tap-triggered date glance that displays a large Russo One month/day date for three seconds.
- Added generated Russo One month and day bitmap resources to the Russo watchface package.
- Added a release builder that emits an App Store-ready `Squintless` PBW with the production UUID.

## 1.0.1 - 2026-07-22

- Added the experimental Squintless Russo Edition using official Russo One numerals.
- Restored the experimental Squintless Red Hat Edition for three-way comparison.
- Refined the outlined battery progress bar to use a taller white interior.

## 1.0.0 - 2026-07-17

- Prepared the first public open-source release.
- Added production App Store metadata and artwork.
- Added the Squintless Pebble Time 2 watchface for `emery`.
- Added canonical Squintless numeral assets and bitmap generation tooling.
- Added Red Hat Display licensing documentation for generated store typography.
- Added MIT, OFL, contributing, code of conduct, and security documentation.
