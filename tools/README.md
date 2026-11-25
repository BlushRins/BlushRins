# Profile SVG Build Tools

GitHub renders README SVGs inside `<img>` tags without loading web fonts, so committed cards, pills, and keycaps in `assets/` convert `<text>` elements into vector `<path>` outlines.

## Structure

- `tools/src/` — editable `<text>` SVG templates mirroring the `assets/` directory layout.
- `tools/src/animations/` — source SVGs used to render the looping hero and mascot APNGs.
- `tools/gen.py` — font outlining helper using `fontTools` (`Inter` + `Noto Sans Mono`).
- `tools/build.py` — compiles every template in `tools/src/` into `assets/`.

## Rebuilding after an edit

1. Edit any SVG inside `tools/src/`.
2. Run:

```bash
python3 -I tools/build.py
```

3. Review `git diff assets/` and commit both the source template and regenerated asset.

Set `PROFILE_FONT_ROOT` to use a different font directory with
`inter/Inter.ttc`, `noto/NotoSansMono-Regular.ttf`, and
`noto/NotoSansMono-Bold.ttf`. CI fetches and verifies the pinned font files.
Run `python3 -I tools/build.py --check` to verify the committed outputs and
local README image links.
