# Font tooling: script, checks and quirks

Everything here was tested with fontTools 4.68 and uharfbuzz 0.57 on a 4-axis variable font, using the real Chromium and WebKit runs described in verification.md.

## The script: `scripts/subset-fonts.py`

Copy it into the project's `scripts/` folder, then edit `ROOT`-relative paths, `OUT_DIR`, `CSS_OUT`, `URL_PREFIX` and `CONFIG`. Each `CONFIG` entry is one face: one source file, which may be variable. Every value must come from the audit.

```bash
uv run scripts/subset-fonts.py                         # build + check, exits 1 on any failed check
uv run scripts/subset-fonts.py --check-coverage dist/  # characters in a build that no file covers
```

The script does the following for each face:

1. Instances the font: `instancer.instantiateVariableFont(font, {"wght": (400, 700), "GRAD": None})`. A tuple limits a range, a number pins, and `None` pins at the default. Every axis must be listed, and the script refuses to guess.
2. Plans the split (core = `CORE` ∩ font, extended = the rest) and promotes characters for cross-split shaping (below).
3. Subsets each part: `layout_features` from the config, `hinting=False`, `desubroutinize`, all name records kept, `notdef_outline`, WOFF2.
4. Copies back `trak` and warns about dropped AAT tables (below).
5. Renames the font if it has a Reserved Font Name (below).
6. Saves the file under a content-hashed name, deletes the stale hash, and writes the `@font-face` CSS with `unicode-range` taken from the actual cmap.
7. Runs the checks.

## Inspect a font

Use this for the Phase 1 measurements, before and after:

```python
# uv run --with 'fonttools[woff]' python inspect.py font.woff2
import sys
from fontTools.ttLib import TTFont
f = TTFont(sys.argv[1])
print("glyphs", f["maxp"].numGlyphs, "| cmap", len(f.getBestCmap()))
if "fvar" in f:
    print("axes", [(a.axisTag, a.minValue, a.defaultValue, a.maxValue) for a in f["fvar"].axes])
    print("instances", len(f["fvar"].instances))
for t in ("GSUB", "GPOS"):
    if t in f:
        print(t, sorted({r.FeatureTag for r in f[t].table.FeatureList.FeatureRecord}))
print("hinting", [t for t in ("fpgm", "prep", "cvt ", "hdmx", "VDMX", "LTSH", "cvar") if t in f]
      or ("CFF hints?" if "CFF " in f or "CFF2" in f else "none"))
print("AAT", [t for t in ("morx", "kerx", "trak", "mort") if t in f])
print("tables", sorted(f.keys()))
print("license", f["name"].getDebugName(13), f["name"].getDebugName(14))
```

## Checks the script runs, and why

| Check | Catches |
| --- | --- |
| The cmap holds exactly the planned codepoints, and `unicode-range` equals the cmap | Ranges promising glyphs the file lacks. The browser downloads the file, finds no glyph, and falls back |
| Vertical metrics (`unitsPerEm`, `hhea`, `OS/2` typo and win metrics, `USE_TYPO_METRICS`) unchanged | Line-height and baseline shifts |
| No hinting tables left | `--no-hinting` silently not applied |
| GSUB/GPOS features ⊆ plan | Features leaking through |
| Advances and outlines vs the source at every corner and midpoint of the kept axis ranges | Instancing errors. Expect small rounding (below) |
| No Reserved Font Name left outside name IDs 0, 7, 13, 14 | Incomplete renames |

## Quirks found in testing

**1. The subsetter silently drops tables it can't subset.** It prints `NOT subset; don't know how to subset; dropped` as a warning. What matters:
- **`trak`** (Apple tracking): **WebKit applies it.** Dropping it changed letter spacing on every line in WebKit, about 20,000 px of diff per screenshot, while Chromium showed nothing. The table has no glyph references, so the script copies it back after subsetting.
- **`morx`/`kerx`/`mort`/`kern`** (AAT shaping and kerning): Safari uses them in place of GSUB/GPOS when they're present. They reference glyph IDs, so they can't simply be copied back. The script warns. Diff in WebKit. If shaping changed, the options are `retain_gids=True` plus copying the tables back (costs bytes; verify) or accepting GSUB/GPOS shaping with the user's approval.
- `MERG`, `meta`, `DSIG`: no effect on rendering.

Never set `passthrough_tables=True` globally. It would also pass glyph-ID-dependent tables through unchanged, which corrupts them after the glyphs are renumbered.

**2. Narrowing an axis range rounds outlines and advances.** The instancer rescales `gvar`/`HVAR` deltas for the new range and rounds them to integers. In testing, glyphs between masters moved by up to 2 font units (2048 UPM) and advances by 1 unit. On screen that showed up as anti-aliasing differences along glyph edges at weights 600 and 700, with no change in glyph positions. That's harmless sub-pixel rounding, but **confirm it in the pixel diffs**: positions unchanged, only edge pixels differ, no line break moved. Since 1-unit advance changes accumulate along a line, a line that was within a pixel of wrapping could wrap differently. Pinning an axis at its default and limiting a range that has no intermediate masters did not round.

**3. Narrowing doesn't always save bytes.** In testing, narrowing `wght` to 400–700 cut the core file from 41.5 KB to 27 KB. Narrowing `opsz` saved nothing: the file got 0.2 KB bigger. Build with and without each limit and keep only the limits that pay off.

**4. `STAT` keeps records for pinned axes.** This is harmless. Browsers don't read `STAT` for matching. Leave it.

**5. The instancer can move the default.** Limiting a range that excludes the old default sets the new default to the nearest bound. That's fine for rendering, because the browser sets every axis explicitly, but the check compares at explicit locations for this reason.

**6. Composite glyphs.** Outline comparisons must decompose components (`DecomposingRecordingPen`). Otherwise accented letters compare their component references and not their shapes.

**7. Speed.** Instancing a large source font to static for each check location is slow, minutes for an 8 MB font. The check subsets the source to the kept characters first, which doesn't change outlines, advances or variations, and that brings it down to seconds.

**8. The source may lack characters you asked for.** For example U+00AD or U+0149 in Latin-1 and Latin Extended-A, or CJK. The script lists them and leaves them out of both the file and its `unicode-range`. They fall back exactly as they do today.

## Cross-split shaping

Browsers shape each font's run separately. When the content puts a core character next to an extended one ("Té", "fé", "rø"), kerning, ligatures and contextual alternates between them are lost. In testing, one lost "T|é" kerning pair shifted the rest of the line, and pixel diffs lit up from that point on.

`plan_split()` reads the audit's `.pairs.txt`, shapes each boundary pair with HarfBuzz both together and separately at every corner of the axis ranges, and when they differ:

- `promote_cross_split: True` (default): moves the extended character into core, then repeats, because a promoted character can now border another extended character. It prints what moved. Report the byte cost.
- `False`: only with the user's approval. It prints the pairs that will render differently.

Limits: only adjacent pairs inside one text node are checked. Pairs that span element boundaries in the same font (`T<span>é</span>`) aren't, so the pixel diffs remain the final check. Features that CSS enables beyond the defaults aren't shaped in the check either.

## Reserved Font Names (OFL)

If the license text says "with Reserved Font Name X", a subset counts as a Modified Version and must not use X in its font names. Check `OFL.txt` and name IDs 13 and 14. Fonts without an RFN (many Google Fonts releases) need no rename.

`rename_reserved()` keeps English name records only. It replaces the RFN, both with spaces and without (as PostScript names write it), in **every** record except copyright (0), trademark (7), and the license text and URL (13, 14), which the OFL requires you to keep. That includes the per-instance PostScript names at IDs 256 and up, which a plain search-and-replace of IDs 1, 4 and 6 misses. Then the check fails if the RFN survives anywhere else.

Only the font's internal names change. The CSS `font-family` alias in `@font-face` stays the same, so no stylesheet changes.
