---
name: typography
description: Apply professional typography principles when generating documents, web pages, presentations, or any formatted text output. Use this skill when creating or reviewing HTML/CSS, print documents, resumes, letters, reports, slide decks, emails, or any content where typographic quality matters. Also use when the user asks about font choices, text formatting, spacing, layout, or typographic best practices.
---

# Typography

Professional typography guidelines based on Butterick's Practical Typography. Apply these rules when generating any formatted output.

## Core Principle

Body text is the most important element — it comprises the majority of any document. Get body text right first, then style everything else relative to it.

## The Four Pillars of Body Text

### 1. Point Size
- **Print**: 10–12 pt
- **Web**: 15–25 px
- Different fonts render differently at the same size — adjust visually

### 2. Line Spacing
- **120–145%** of point size (e.g., 12 pt text → 14.4–17.4 pt leading)
- CSS: use unitless `line-height` (e.g., `1.3`–`1.45`)
- Never rely on "Single" or "1.5 lines" presets in word processors

### 3. Line Length
- **45–90 characters** per line (including spaces)
- Quick test: 2–3 lowercase alphabets should fit on one line
- Control via margins, not paragraph indents
- Web: prevent text from spanning full browser width

### 4. Font Choice
- Use professional fonts over system defaults
- Avoid Times New Roman and Arial for final documents
- See [references/fonts.md](references/fonts.md) for font guidance

## Type Composition Rules

### Quotation Marks
- Always use curly quotes (" " ' '), never straight quotes (" ')
- Exception: foot/inch marks remain straight

### Dashes
- **Hyphen** (`-`): compound words, line breaks
- **En dash** (`–`): ranges (1990–2000, pp. 10–15), connections (liberal–conservative)
- **Em dash** (`—`): parenthetical breaks — stronger than commas, lighter than parentheses
- Never approximate with double hyphens (`--`)

### Spacing
- One space between sentences — never two
- No consecutive whitespace characters
- Use nonbreaking spaces after paragraph/section marks (§, ¶)

### Special Characters
- Use proper ellipsis (…), not three periods
- Use proper trademark (™), copyright (©), registered (®) symbols
- Apostrophes curve downward (it's, not it's with a straight mark)
- Limit exclamation points to one per document over three pages

## Text Formatting

### Emphasis
- Bold and italic are **mutually exclusive** — never combine
- Use both sparingly; when everything is emphasized, nothing is
- With serif fonts: italic for gentle emphasis, bold for strong
- With sans serif: prefer bold (italic is barely noticeable)
- Adjacent punctuation stays unformatted

### Headings
- Limit to 2–3 levels maximum
- Prefer bold over italic; avoid all-caps and underlining
- Use subtle size increases (0.5–1 pt over body text, not dramatic jumps)
- Emphasize via space above/below rather than large size changes
- Suppress hyphenation in headings

### ALL CAPS and Small Caps
- All caps: acceptable for less than one line of text
- Add 5–12% letterspacing to all-caps and small-caps text
- Always enable kerning
- Only use real small caps (OpenType `smcp` feature), never faked

### Underlining
- Avoid entirely except for web hyperlinks

### Color
- **Print body text**: always black
- **Web body text**: consider dark gray over pure black
- Use color idiomatically for links; don't color non-clickable text
- Restraint is key — color for emphasis fails at body-text sizes

## Page Layout

For detailed layout rules, see [references/layout.md](references/layout.md).

### Key Layout Rules
- First-line indents OR space between paragraphs — never both
- First-line indent size: 1–4× the point size
- Print margins: typically 1.5–2.0" at 12 pt for proper line length
- Justified text requires hyphenation; prefer left-aligned in word processors and web
- Mixing fonts: maximum 2 (rarely 3); assign each a consistent role
- Keep fonts in separate paragraphs; avoid multiple fonts in one paragraph

### Maxims
1. Design body text first
2. Divide page into foreground and background
3. Adjust in smallest visible increments
4. When in doubt, try it both ways
5. Same things look the same; different things look different
6. Embrace simplicity — fewer fonts, fewer colors
7. Respect white space

## Web-Specific Guidelines

- Body text: 15–25 px
- Use `line-height` with unitless values
- Control line length with `max-width` (e.g., `max-width: 33em`)
- Use `text-indent` for first-line indents, not margins
- Use `letter-spacing: 0.05em`–`0.12em` for caps/small-caps
- Use CSS `font-variant: small-caps` for real small caps
- Table cell padding: start at ~3px, increase incrementally
- Use `<ul>`/`<ol>` for lists, never manual bullets

## Document-Specific Notes

For tables, lists, block quotations, and sample document guidance, see [references/elements.md](references/elements.md).
