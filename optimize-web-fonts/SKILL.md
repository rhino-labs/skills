---
name: optimize-web-fonts
description: Make a site's self-hosted web fonts load faster without changing how anything renders. Measures the current fonts and per-page font bytes, audits exactly which characters, weights, axis values and OpenType features the site uses, then subsets, instances and splits each font into a preloaded core file and a unicode-range extended file via a hand-run script. Proves the result with before/after pixel diffs. Use when the user wants smaller font files, faster font loading, font subsetting, unicode-range splitting, trimming variable font axes, or asks why their fonts are so heavy. Not for changing typefaces, font-display, or fallback fonts.
---

# Optimize Web Fonts

## Overview

Shrink font bytes as far as possible while keeping rendering **pixel-identical**. The deliverables:

1. A hand-run script, committed, that turns the original font files into subset, instanced and split WOFF2 files plus their `@font-face` rules.
2. The generated files, committed.
3. Before and after measurements and pixel diffs that prove nothing changed visually.

Read the references when you reach the matching phase:

- `references/usage-audit.md`: how to find what the site actually uses (characters, weights, axes, features, CSS side effects).
- `references/font-tooling.md`: the subset script, its checks, the tool quirks found in testing, cross-split shaping, and renaming fonts with a Reserved Font Name.
- `references/verification.md`: measuring bytes per page and preloads, building a baseline, pixel-diffing, and classifying differences.

Tested scripts to copy into the project's `scripts/` folder and adapt. All run with `uv run` and need no project dependencies:

- `scripts/audit-font-usage.py`: rendered-pass usage audit (Playwright).
- `scripts/subset-fonts.py`: the hand-run instance, subset, split and check script. This is the committed deliverable.
- `scripts/compare-fonts.py`: `measure` (font bytes, requests and preloads per page) and `diff` (Chromium and WebKit pixel diffs).

## Ground rules

These come from the user's brief. Don't relax them without approval.

1. **Any visual change is a regression unless the user approves it.** When an optimization would change rendering, don't apply it by default. Report what it saves and what it changes, and let the user decide.
2. **Keep the current loading behavior.** Don't change `font-display`, fallback fonts, generated fallback faces (`size-adjust` and similar), or the `font-family` stacks, except as needed to keep the core and extended files in one family (see Phase 5).
3. **Nothing in the build.** Don't add font processing to the build, bundler plugins, CI steps, or postinstall hooks. Write a script the user runs by hand, commit its output, and document when it needs rerunning.
4. **Keep the originals.** Commit the unmodified source fonts where they aren't served (for example `fonts/source/`), so the script can always be rerun from the originals and never from its own output.
5. **Don't trust font tools.** Inspect every generated file (Phase 4) before wiring it in.

## Phase 0: Set up the baseline

The baseline must use **the same content** as the optimized build, so content changes can't hide or fake differences.

- Do the work on a branch. Create a `git worktree` of the starting commit for the baseline. As long as you only touch font files, `@font-face` CSS, preloads and the new script, the content stays identical.
- Build and serve both versions with the same production command, on two ports, at the same time.
- If content changes during the work, rebuild the baseline from the merge base with the current content checked in, and say so in the report.

## Phase 1: Measure the current state

Record all of this before changing anything. Put the numbers in the final report.

**Per font file:** path, format, bytes, glyph count, cmap size, variable axes (tag, min, default, max), named instances, GSUB and GPOS feature tags, whether it's hinted (`fpgm`, `prep`, `cvt `, `hdmx`, `VDMX`, `LTSH`, `cvar`, or CFF hints), other tables present (especially AAT tables: `morx`, `kerx`, `trak`), vertical metrics, and license. For the license, check for an OFL **Reserved Font Name** in the license file or name IDs 13 and 14. See `references/font-tooling.md`, "Inspect a font".

**Per page**, in a real browser with no cache: every font request (URL and bytes transferred), total font bytes, and every `<link rel="preload" as="font">`, including whether each preload is actually used. See `references/verification.md`, "Measure bytes per page".

**How fonts are declared:** where the `@font-face` rules live, their descriptors (`font-weight` ranges, `font-style`, `font-stretch`, `font-display`, any existing `unicode-range`), how the framework emits them (plain CSS, `next/font`, Fontsource, a CSS-in-JS global), and any generated fallback faces.

Build the list of pages to test now. It must cover all of these: pages with **code** (monospace), **italics** (including bold inside italics), **accented characters**, **components with their own font settings** (inline styles, CSS-in-JS, utility classes), and **CJK** text. Add the home page and the heaviest template of each kind.

## Phase 2: Find out what the site actually uses

Follow `references/usage-audit.md`. Run two passes and combine the results:

1. **A rendered pass** (`scripts/audit-font-usage.py`). Crawl every page of the built site in a browser at mobile and desktop widths. Walk every text node and pseudo-element and read its computed font properties. Computed styles catch inline component styles, CSS-in-JS and utility classes without you having to find them. The script also records adjacent character pairs for the cross-split shaping check.
2. **A static pass.** Grep stylesheets, component files and inline `style` attributes for anything the crawl can't see: `:hover`, `:focus` and other state styles, content that only appears after interaction (menus, modals, toasts, tooltips), JS-inserted text, and breakpoints you didn't render.

For **each font** (family and style), the output is:

- **Characters** rendered in it, after `text-transform`, plus characters CSS creates: `hyphens: auto` inserts **U+2010** (hyphen), `text-overflow: ellipsis` inserts U+2026, list markers, `quotes` on `<q>`, `content:` strings, and counters.
- **Axis values** per axis: every computed `font-weight` (including one-offs, `bolder`, and **bold inside italics**), `font-stretch`, every `font-variation-settings` value, and the font-size range when `font-optical-sizing: auto` drives `opsz`.
- **OpenType features** in use: browser defaults that are on unless something turns them off (`kern`, `liga`, `clig`, `calt`, `locl`, `ccmp`, `mark`, `mkmk`, `rlig`, `rvrn`, and `curs`/`dist` when present), plus everything turned on by `font-feature-settings`, `font-variant-*`, and `font-kerning`.
- **What currently falls back.** Characters the font doesn't contain today (CJK, for example) render with system fonts. That must stay true.

## Phase 3: Plan the cut

Write the plan as a table per font: what is kept, what is dropped, and the expected bytes. Apply these rules:

- **Characters:** keep every used character, plus all of Latin-1 Supplement (U+00A0–00FF) and Latin Extended-A (U+0100–017F), plus CSS-inserted characters such as U+2010 when `hyphens: auto` is used. Keep only characters the source font actually contains. If CJK renders with system fonts today, it stays that way: never add CJK. If the web font itself contains CJK, ask before touching it.
- **Variable axes:** limit each axis to the minimum and maximum values in use. **Fix an axis at one value only if nothing anywhere overrides it**: no `font-variation-settings`, no other weight, no state style, no component override. Make the `@font-face` descriptors (`font-weight: 400 700`, `font-stretch`) match the new ranges, so browser font matching resolves exactly as before. A requested weight outside the descriptor range gets clamped, which changes rendering.
  - **Measure each limit separately, and keep only the ones that save bytes.** Narrowing a range makes the instancer re-round outlines and advances, by up to about 2 and 1 font units. Narrowing `wght` saved 35% in testing. Narrowing `opsz` saved nothing, so it wasn't worth the rounding.
- **OpenType features:** keep the browser defaults plus the features in use. Drop the rest. A feature counts as in use if any CSS turns it on, even on one component.
- **Hinting:** drop it. Pixel diffs on macOS and Linux can't show hinting changes, because macOS ignores TrueType hinting. Report it as **unverified on Windows** unless you test there.
- **Split** each font into two files:
  - **Core:** ASCII (U+0020–007E) plus the punctuation most pages use. Start from curly quotes (U+2018, U+2019, U+201C, U+201D), dashes (U+2013, U+2014) and ellipsis (U+2026). Add any other character the audit finds on most pages (NBSP U+00A0 is common). Core gets preloaded.
  - **Extended:** everything else that was kept, behind `unicode-range`, so it only downloads on pages that render one of its characters. Never preload it.
  - Characters in the two files must not overlap. Each file's `unicode-range` lists **only codepoints its cmap actually contains**, generated from the output file and never typed by hand.
- **Shaping across the split.** Browsers shape each font's run separately, so kerning, ligatures, contextual alternates and mark attachment don't work between a core character and an extended one. For example, kerning between `T` and `é` is lost, and the rest of the line shifts. `subset-fonts.py` shapes every boundary pair from the audit with HarfBuzz and, by default, moves affected extended characters into core. Report what moved and what it cost. Accepting the loss instead needs the user's approval.

Present the plan, including every point where the brief and the font conflict, before you build anything that changes rendering.

## Phase 4: Write the script, run it, check the output

Copy `scripts/subset-fonts.py` into the project and adapt it (Python with fontTools and uharfbuzz, run with `uv run`, dependencies pinned with inline PEP 723 metadata). Keep its config next to it and commit the audit's character and pair files. The script:

1. Reads its config: source font paths, axis limits, features, the audit's character and pair files, output paths, and the `@font-face` descriptors copied exactly from the current CSS.
2. Instances, plans the split (including cross-split promotion), subsets, and saves WOFF2 under content-hashed filenames. Use the site's existing cache-busting convention if it has one.
3. Copies back `trak` and warns about dropped AAT tables (`morx`, `kerx`).
4. Renames the font internally if its license has a Reserved Font Name. The CSS `font-family` alias stays the same, so the site doesn't change.
5. Writes a generated CSS file with the `@font-face` rules and the exact `unicode-range` for each file, plus a header comment saying it's generated and how to regenerate it.
6. Checks every generated file and exits non-zero if any check fails:
   - The cmap matches the plan, and `unicode-range` equals the cmap.
   - Vertical metrics are unchanged.
   - No hinting is left.
   - The features match the plan.
   - Advances and outlines match the source at every corner and midpoint of the axis ranges, within rounding (≤ 2 units for outlines, ≤ 1 for advances).
   - The Reserved Font Name appears nowhere outside the copyright, trademark and license records.

Read every warning it prints. Report each dropped table and each character the source didn't contain. See `references/font-tooling.md` for what each one means.

Document **when to rerun** in the script header and in a README next to the fonts:

- New content uses a character the fonts don't cover. The script's check mode lists uncovered characters for a given build.
- The site uses a new weight, style, axis value, `font-variation-settings` value or OpenType feature.
- Optical sizing is on and the site uses a font size outside the `opsz` range.
- A source font is upgraded or added.
- The core punctuation set needs to change.

## Phase 5: Wire it in without changing behavior

- **Use one family name for both files.** Write two `@font-face` rules with the same `font-family`, the same descriptors and the same `font-display`. They differ only in `src` and `unicode-range`. Don't make core and extended separate families in a font stack.
- **Watch for generated fallback faces.** If the framework generates a metric-matched fallback face (`next/font`'s `"X Fallback"`, fontaine, Capsize and similar), it covers every character. If it sits *between* the core and extended files in the stack, it draws the extended characters before the real font does, and the extended file may never load. Make sure the fallback comes after the shared family, exactly where it was before. If the framework can't emit `unicode-range` (for example `next/font/local`), move these faces to plain CSS and leave the fallback face as it was. Explain this in the report.
- **Preload core only**, with `<link rel="preload" as="font" type="font/woff2" crossorigin>`. The URL must exactly match the `@font-face` `src`, or the font downloads twice. Preload the same faces that are preloaded today, swapped for their core files. Don't add preloads for faces that weren't preloaded before.
- Delete the old served font files only after the diffs pass. Keep the originals in `fonts/source/`.

## Phase 6: Verify

Follow `references/verification.md` and use `scripts/compare-fonts.py`.

1. **Pixel-diff** the baseline against the optimized build. Cover every test page from Phase 1, in **Chromium and WebKit**, at mobile and desktop widths, at 1× and 2× device pixel ratio. Take screenshots only after all font loads have finished, including extended files triggered by layout.
2. **Explain every pixel that differs.** Classify each difference as:
   - **content change**: the baseline wasn't the same content. Fix the baseline and rerun.
   - **regression**: fix it and rerun.
   - **harmless sub-pixel rounding**: show the diff region and explain why. For example: anti-aliasing changed along glyph edges at weights inside a narrowed `wght` range, glyph positions didn't move, and the script reported outline deltas of 2 font units or less.
   A diff you can't explain counts as a regression.
3. **Re-measure bytes per page.** Confirm that each extended file loads **only** on pages that render one of its characters, by cross-checking the network log against the audit. Confirm core files are preloaded and the preloads are used. Confirm CJK pages still render CJK with system fonts and no new font requests.

## Report

When done, report:

- **Bytes per font file**, before and after, for core and extended.
- **Font bytes per page**, before and after, and which pages load extended files.
- **Pixel-diff results**: pages × browsers × viewports, how many pixels differed, and the classification of every difference.
- **Deviations from the brief and their cost.** Examples: hinting dropped but unverified on Windows; characters moved to core to keep cross-file kerning (+N bytes); faces moved out of the framework font loader to emit `unicode-range`; an axis kept wider than planned because of an override.
- **Changes you didn't make** because they would change rendering, with what each would save.
- **How to rerun**: the exact command, inputs, and the rerun triggers.
- **Later** (suggest only, don't implement): embedding the core font as a data URI in the global stylesheet to remove a request, and precaching extended files after idle (`requestIdleCallback` plus `FontFace.load()` or `<link rel="prefetch">`).
