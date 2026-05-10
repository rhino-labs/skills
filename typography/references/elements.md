# Document Elements Reference

## Table of Contents
- [Block Quotations](#block-quotations)
- [Lists](#lists)
- [Tables](#tables)
- [Rules and Borders](#rules-and-borders)
- [Character Reference](#character-reference)

## Block Quotations

- Reduce point size and line spacing slightly from body text
- Indent 0.5–1" on the left (optionally right too); on web use 2–5 em
- Omit quotation marks — the indentation signals a quote
- Avoid overuse — readers perceive block quotes as skippable filler
- Better approach: edit quoted material and weave it into prose

## Lists

- Always use automated list formatting (`<ul>`, `<ol>`), never manual bullets
- Asterisks (*) are inadequate as bullets — too small, positioned too high
- Bullet size should be noticeable but not oversized; hollow bullets can be subtler
- List indices (numbers/bullets) can use a different font or smaller size than list text
- Dingbat geometric shapes work better than pictorial ones at small sizes

## Tables

### Cell Borders
- Turn off all borders first — text creates an implied grid
- Re-add borders only where needed for legibility
- Tables with many small cells become cluttered with full borders

### Cell Padding
- Start at ~0.03" (or ~3px on web) and increase in small increments
- Top/bottom padding can differ from left/right
- Generous vertical padding helps dense tables breathe

### Implementation
- CSS: use `padding` on `td`/`th` elements
- Use `border-collapse: collapse` for clean borders
- Consider alternating row backgrounds instead of borders for large data tables

## Rules and Borders

- Horizontal rules can separate sections but use sparingly
- Thinner rules (0.5–1 pt) are more refined than thick ones
- Borders on text blocks work like block quotation indents — use for emphasis

## Character Reference

| Character | Windows | Mac | HTML |
|-----------|---------|-----|------|
| Opening double quote " | Alt 0147 | Opt + [ | `&ldquo;` |
| Closing double quote " | Alt 0148 | Opt + Shift + [ | `&rdquo;` |
| Opening single quote ' | Alt 0145 | Opt + ] | `&lsquo;` |
| Closing single quote ' | Alt 0146 | Opt + Shift + ] | `&rsquo;` |
| En dash – | Alt 0150 | Opt + hyphen | `&ndash;` |
| Em dash — | Alt 0151 | Opt + Shift + hyphen | `&mdash;` |
| Ellipsis … | Alt 0133 | Opt + ; | `&hellip;` |
| Trademark ™ | Alt 0153 | Opt + 2 | `&trade;` |
| Copyright © | Alt 0169 | Opt + G | `&copy;` |
| Registered ® | Alt 0174 | Opt + R | `&reg;` |
| Section § | Alt 0167 | Opt + 6 | `&sect;` |
| Paragraph ¶ | Alt 0182 | Opt + 7 | `&para;` |
| Nonbreaking space | Ctrl+Shift+Space | Opt + Space | `&nbsp;` |
