# Page Layout Reference

## Table of Contents
- [Margins](#margins)
- [Paragraphs](#paragraphs)
- [Justified vs Left-Aligned](#justified-vs-left-aligned)
- [Hyphenation](#hyphenation)
- [Columns](#columns)
- [Widows and Orphans](#widows-and-orphans)
- [Grids](#grids)
- [Web Layout](#web-layout)

## Margins

### Print
- Default 1" margins produce lines that are too long for proportional fonts
- At 12 pt: use 1.5–2.0" left/right margins
- Adjust margins based on point size — smaller fonts need wider margins
- Bottom margin can be ~0.25" larger than top to visually center text
- Asymmetric left/right margins: make the difference at least 1"
- Gutter margins: add extra inner-edge space for bound documents

### Web
- Apply the same line-length principles as print
- Use `max-width` on text containers (e.g., `33em`) rather than percentage widths
- Generous margins/padding on mobile and desktop

## Paragraphs

### Indents vs Spacing
- Use first-line indents OR space between paragraphs — never both
- **First-line indent**: 1–4× the point size (12 pt text → 12–48 pt indent, or 0.17–0.67")
- Narrower text blocks (≤3") need smaller indents
- First paragraph indent is optional (the start is already obvious)
- **Space between**: 4–10 pt; keep less than one full line to avoid looking like a gap

### Implementation
- Never use spaces or tabs for indentation
- Word: Paragraph → Indents and Spacing → Special → First line
- CSS: `text-indent` property
- Use hanging indents (negative values) only with visual markers like bullets

## Justified vs Left-Aligned

- Justified: cleaner, more formal look with even edges
- Left-aligned: straight left edge, ragged right
- **Justified requires hyphenation** — without it, word spacing becomes erratic
- Word processors and browsers have rudimentary justification engines
- Prefer left-aligned in word processors and on the web
- Professional layout software (InDesign) handles justification better
- Never letterspacing to justify — distribute space between words only

## Hyphenation

- Always enable with justified text
- Optional but helpful with left-aligned text
- Suppress in headings
- Use optional/soft hyphens for manual control when needed

## Columns

- Useful for achieving proper line length on wide pages
- Maintain 45–90 character line length within each column
- Add sufficient gutter space between columns

## Widows and Orphans

- **Widow**: last line of a paragraph stranded at the top of a page
- **Orphan**: first line of a paragraph stranded at the bottom of a page
- Enable widow/orphan control in word processors
- Use "keep lines together" and "keep with next paragraph" for headings

## Grids

- Use grids to relate elements systematically on complex layouts
- Grids help maintain consistency across pages
- Not necessary for simple, single-column documents

## Web Layout

- Break the five bad habits:
  1. Don't use tiny body text
  2. Don't use oversized headings
  3. Don't limit yourself to system fonts
  4. Don't clutter edges with navigation
  5. Don't build with large blocks of solid color
- Draw visual inspiration from print design, posters, and other media
- Design intentionally rather than following template conventions
