# Verification: bytes per page and pixel diffs

Both are done by `scripts/compare-fonts.py` (Playwright + Pillow, run with `uv run`). Install the browsers once:

```bash
uv run --with playwright==1.64.1 playwright install chromium webkit
```

## Build the baseline

```bash
git worktree add ../site-baseline <starting-commit>
(cd ../site-baseline && <install> && <production build> && <serve on :4100>)
<production build> && <serve on :4173>          # the optimized branch
```

Same content, same build command, both served at once. If the site pulls content from a CMS or API, freeze it: use the same snapshot or env for both, or the diffs will show content changes.

## Measure bytes per page

```bash
uv run scripts/compare-fonts.py measure --base http://localhost:4100 --pages pages.txt --out fonts/report/before.json
uv run scripts/compare-fonts.py measure --base http://localhost:4173 --pages pages.txt --out fonts/report/after.json
```

The script loads each page in a fresh browser context (empty cache), scrolls through it so lazy content requests its fonts, and records the following:

- Every font request and its encoded bytes (`PerformanceResourceTiming.encodedBodySize`). If the server sends fonts cross-origin without `Timing-Allow-Origin`, this reads 0. In that case, measure from the files on disk.
- Total font bytes for the page.
- `<link rel="preload" as="font">` elements with their `crossorigin` and `type` attributes.
- Which `FontFace`s actually loaded, including their `unicode-range`.
- Chrome's console warnings about preloads that weren't used, or that were requested twice because of a missing `crossorigin` or a URL mismatch.

Confirm all of the following:

- **Extended files load only on pages that render one of their characters.** Cross-check with `usage.json`. An extended file loading on an ASCII-only page means a `unicode-range` is too wide, or some text in that face contains a character you didn't expect. Find it: often U+00A0, a curly apostrophe in a footer, or `©`.
- **Each core file is preloaded and used**, with no preload warnings.
- **CJK pages load no new font files.** CJK still renders with system fonts.

## Pixel diffs

```bash
uv run scripts/compare-fonts.py diff --before http://localhost:4100 --after http://localhost:4173 \
    --pages pages.txt --out fonts/report/diff
```

Each page is captured in Chromium and WebKit, at 390px and 1280px wide, at 1× and 2× device pixel ratio, as a full-page screenshot. Before each capture the script disables animations, transitions and the caret, waits for `document.fonts.ready`, scrolls the page so lazily triggered `unicode-range` loads happen, then waits for the network to go idle and for fonts again. Output per shot: the changed pixel count, the bounding box, the maximum channel delta, and a `.diff.png` that paints changed pixels red over a faded copy of the "after" shot. Identical shots are deleted. `summary.json` collects everything.

Don't skip WebKit. Some regressions only show there: a dropped `trak` table changed spacing on every line in WebKit while Chromium was clean.

The page list must include pages with code, italics (including bold inside italics), accented characters, components with their own font settings, and CJK. Diff the whole page list, not just the samples, if it's small enough.

## Classifying differences

Open every `.diff.png`, crop to the bounding box, and look. Use the pattern to tell the categories apart:

| Pattern in the diff | Likely cause | Classification |
| --- | --- | --- |
| Text from a certain character onward shifts sideways; the rest of the line is solid red | Kerning or shaping lost across the core/extended split, or a changed advance width | **Regression.** Promote the character to core (`promote_cross_split`), or check the advance check |
| Every line in WebKit only is slightly wider or narrower | `trak` (or `kerx`/`morx`) dropped | **Regression.** See font-tooling.md quirk 1 |
| Thin red outlines along glyph edges at some weights, no shift in position, the same in both engines | Outline rounding from narrowing an axis range | **Harmless sub-pixel rounding.** Confirm the script's reported deltas are ≤ 2 units and ≤ 1 unit |
| A glyph changes shape (different `a`, different digits, lost ligature) | A feature dropped that CSS or the defaults use | **Regression.** Add the feature back |
| A glyph renders in a different typeface | The character is missing from both files, or `unicode-range` is wrong | **Regression.** Check the cmap, the range, and whether a generated fallback face sits between core and extended |
| Bold looks smeared or faked in italics | Italic `wght` range or `font-weight` descriptor too narrow, so the browser synthesizes bold | **Regression.** Widen the italic range |
| Line breaks moved | Accumulated advance rounding, or a different glyph | **Regression** unless the user approves it |
| Differences in timestamps, randomized content, ads | Content differs | **Content change.** Freeze it and rerun |
| Whole page offset | Layout or content change outside the fonts | Investigate; not a font result |

Every difference must end up in one of these categories with a short reason. Any you can't explain count as regressions. In the report, list the shots, the counts, and the classification of each group of differences, and attach crops for the rounding cases so the user can judge them.
