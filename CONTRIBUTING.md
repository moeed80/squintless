# Contributing to Squintless

Thanks for helping make Squintless better.

Squintless is an accessibility-first Pebble Time 2 watch face. Contributions should protect that purpose: instant readability with no unnecessary information.

## Priorities

- Preserve the simple hours, battery, minutes layout.
- Prefer readability over decoration.
- Keep Pebble Time 2 support focused on `emery`.
- Keep numeral design changes in `typeface/`.
- Keep watchface rendering changes in `watchface/`.

## Development

Regenerate watchface assets after changing numeral SVGs:

```sh
python3 typeface/tools/generate_watchface_assets.py
```

Generate store artwork and the Pebble menu icon:

```sh
python3 tools/generate_store_assets.py
```

Build the watchface:

```sh
cd watchface
pebble build
```

## Pull Requests

Before opening a pull request:

- Run the relevant generators.
- Build the Pebble package.
- Check the generated screenshots or previews visually.
- Explain any accessibility tradeoffs in the PR description.

## Licensing

By contributing, you agree that your contribution is licensed under the MIT License unless it explicitly modifies third-party font files. Red Hat Display and any modified font files remain under the SIL Open Font License.
