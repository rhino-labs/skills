# Usage audit: what the site actually asks of each font

The goal is a per-face list of characters, axis values, features and pairs that is **complete**. A missing character becomes a fallback-font glyph. A missing weight becomes a clamped or synthesized weight. A missing feature changes glyph shapes. Overestimating only costs bytes, so when in doubt, include it.

## 1. Rendered pass: `scripts/audit-font-usage.py`

Copy the script into the project's `scripts/` folder and run it against a production build. A dev server can inject different markup or styles.

```bash
uv run scripts/audit-font-usage.py --base http://localhost:4173 --sitemap --out fonts/usage
# or --pages pages.txt, one path per line
```

It loads every page at 375, 768, 1280 and 1920px wide. It walks every text node, `::before`/`::after` content, list markers, `<q>` quotes and form-control values and placeholders, and records the **computed** style of each. Computed styles already include inline `style` attributes, CSS-in-JS, utility classes and media queries for the widths it renders. That makes this pass the source of truth for components that set their own fonts.

It writes the following:

- `usage.json`, one entry per face keyed `family|style`:
  - `chars`: every character, after `text-transform`, plus the CSS-inserted characters listed below.
  - `weights`, `stretch`, `sizes` (min and max), `variation` (every `font-variation-settings`), `features` (every `font-feature-settings`), `variants` (`font-variant-*` values), `opticalSizing`, `kerning`, `synthesis`.
  - `examples`: one element selector per unusual combination of settings, so you can trace a one-off override back to its component.
  - `non_ascii_by_pages`: how many pages use each non-ASCII character. Use it to decide what goes in core.
- `<family>-<style>.txt`: the characters, input for `subset-fonts.py`.
- `<family>-<style>.pairs.txt`: adjacent character pairs that involve a non-ASCII character, input for the cross-split shaping check.

How to read the faces:

- **`Family|italic` with no italic `@font-face`** means the browser synthesizes the italic from the upright file. The upright file must then cover those characters and weights too. Synthesis must stay possible, so keep `font-synthesis` as it is.
- **Bold inside italics** appears as `Family|italic` with weight 700 (or 600). The italic face's `wght` range and `font-weight` descriptor must include it. If the italic face is static and has no bold, the browser fakes bold today, and it must keep doing so. Don't add a bold italic.
- **`(no web font)`** means system fonts render that text. Code blocks with a system monospace stack and CJK pages usually land here. Leave it alone.

## 2. Static pass: what the crawl can't see

Grep the source, including components and not only stylesheets, for each of these. Then add what you find to the audit output by hand:

| Look for | Why |
| --- | --- |
| `:hover`, `:focus`, `:active`, `[aria-*]`, `[data-state]` rules that change `font-weight`, `font-variation-settings`, `font-style` or `font-feature-settings` | The crawl doesn't trigger states |
| `font-variation-settings` anywhere, including inline `style={{ fontVariationSettings }}` | Any override blocks pinning that axis |
| Weights in JS: `fontWeight:`, `font-semibold`-style utilities, design tokens, `bolder`/`lighter` | One-off weights extend the range |
| Text that only exists after interaction: menus, dialogs, toasts, tooltips, validation messages, empty and error states, 404 pages, emails rendered as pages | Characters the crawl never saw |
| JS-generated text: dates, relative times (`Intl`), currency and number formatting (`Intl.NumberFormat` emits U+00A0 or U+202F and `−` U+2212 in some locales), pluralized strings, i18n catalogs | Characters that depend on locale or data |
| Markdown or MDX typography plugins (smartypants, remark-smartypants) | Curly quotes, dashes, ellipses, primes (U+2032/2033) |
| `hyphens: auto` | Browsers insert **U+2010** (‐) when the font has it, otherwise `-` |
| `text-overflow: ellipsis`, `-webkit-line-clamp` | Inserts U+2026 |
| `list-style-type`, `::marker`, `counter()` | Bullets (U+2022, U+25E6, U+25AA), digits, custom strings |
| `quotes`, `open-quote`, `<q>` | Language-dependent quotes („“ «» ‹›) |
| `content:` with escapes (`"\2192"`) | Arrows, icons drawn with text |
| `text-transform: uppercase`/`capitalize`, `font-variant-caps` | Uppercase forms (ß→SS, ﬁ→FI), `smcp`/`c2sc` |
| `font-variant-numeric`, `font-feature-settings` (`tnum`, `lnum`, `onum`, `zero`, `ss01`, `case`, `frac`) | Features that must survive the subset, plus the alternate glyphs they reach |
| `font-kerning: none`, `font-variant-ligatures: none` | Features you might be able to drop, but only if every use of the face turns them off |
| `font-optical-sizing` (default `auto`) | `opsz` follows the font size in CSS px: keep the range from the smallest to the largest size the face is used at, including every breakpoint and every `clamp()` bound |
| Whitespace characters in content: U+00A0, U+2009, U+200A, U+202F, U+200B | If the font lacks a space character, the browser falls back for it and the spacing changes |
| `<sup>`/`<sub>`, `font-variant-position` | Firefox uses `sups`/`subs` when the font has them |

## 3. OpenType features

Browsers turn these on by default for horizontal text: `kern`, `liga`, `clig`, `calt`, `locl`, `ccmp`, `mark`, `mkmk`, `rlig`, `rvrn` (needed by variable fonts with feature variations), plus `curs` and `dist` when present. Keep them unless the audit proves a face never renders with them. Add every feature CSS turns on. Drop the rest: stylistic sets, `frac`, `sups`, `smcp` and so on, unless something uses them.

The subsetter keeps glyphs reachable through the features you keep (the glyph closure). For example, `tnum` keeps the tabular digits. You don't have to list alternate glyphs by hand.

## 4. Axis values

For each variable axis, record the minimum and maximum value actually rendered:

- `wght`: every computed `font-weight` for that face, plus `font-variation-settings: "wght" N`.
- `wdth`: `font-stretch` plus `font-variation-settings`.
- `opsz`: the font-size range when `font-optical-sizing: auto`, or explicit settings.
- `slnt`/`ital`: `font-style: oblique <angle>` and italic usage.
- Custom axes (`GRAD`, `XTRA` and so on): only `font-variation-settings` can set them. If nothing sets one, it renders at its default, so pin it with `None` in the config.

**Pin an axis** (a single value) only when the audit and the grep both show nothing overriding it. **Narrow a range** only when doing so saves bytes. Measure each axis separately: narrowing `wght` often saves 30% or more, while narrowing `opsz` can save nothing. Narrowing introduces outline rounding (see font-tooling.md), so don't pay that cost for no gain.

## 5. Choosing the core set

Start from ASCII (U+0020–007E), curly quotes, en and em dashes, and the ellipsis. Then use `non_ascii_by_pages`. A character used on most pages (U+00A0 often is) belongs in core: otherwise most pages download both files. A character used on a few pages belongs in extended. `subset-fonts.py` then moves into core any extended character that would lose kerning or shaping with a core neighbour (see font-tooling.md, "Cross-split shaping").
