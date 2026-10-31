---
name: landing-page
description: Write and build a product landing page in a fixed section order. The sections are a hero (a product + ability + audience headline, three feature checks, a CTA with a risk reducer, and review badges), a logo bar, a customer quote, three industry pain points, three feature buckets (with optional proof quotes between them), and a founder letter. The skill writes the copy first, then builds the page in the project's own stack and design tokens. Use it when the user asks for a landing page, home page, marketing page, product page or sales page, or wants an existing one rewritten or restructured in this format.
---

# Landing page

Build a landing page that makes one argument from top to bottom: what the product is, proof that it works, the problem it solves, how it solves it (three times, each one proven), and the person behind it.

## The format

| # | Section | What it does |
| --- | --- | --- |
| 1 | **Hero** | Kicker (category) · "The **[product]** that enables **[ability]** for **[audience]**" · explainer · 3 feature checks · primary CTA + risk reducer · 3 review badges · visual on the right |
| 2 | **Logo bar** | "These brands enjoy our benefits" plus 4–6 customer logos |
| 3 | **Quote** (accent band) | A customer quote that proves the hero headline |
| 4 | **Pain points** (dark) | "The big industry problem" · a headline summing up the problem · 3 problem cards |
| 5 | **Feature bucket 1** | Visual left · "1. Bucket" · "Gain this **[capability]** with these **[features]**" · body · 3 checks |
| 6 | **Quote** *(optional)* | Proves bucket 1 |
| 7 | **Feature bucket 2** | Same as bucket 1, with the visual on the right |
| 8 | **Quote** *(optional)* | Proves bucket 2 |
| 9 | **Feature bucket 3** | Same as bucket 1, with the visual on the left |
| 10 | **Founder letter** (muted) | A first-person letter in eight beats, with a photo on the right |

**Read `references/sections.md` and `references/formulas.md` before writing anything.** The first has the copy formula, the rules and the layout for every section. The second has the headline formulas for the hero and the pain points section. `assets/template.html` is a working static version of the whole page, tested at 390px and 1280px wide. Use it as the reference for structure and spacing.

Don't change the order and don't add sections unless the user asks. The three problems map onto the three buckets, and each quote proves the section right before it. Moving pieces breaks that argument.

**The quotes between buckets (6 and 8) are optional.** Include one only when there's a real customer quote that proves *that bucket's* claim, and otherwise leave it out. Don't put in a placeholder, and don't stretch a general quote to fit. The page then has 8, 9 or 10 sections. The hero quote (3) is required: use a placeholder if it's missing.

## Two copy principles

Most conversion problems on a landing page come down to one of these two. Every headline on the page has to pass both.

**1. Help visitors skim.** Imagine the page has no paragraph copy at all. Most visitors skim the headlines before they decide whether any paragraph is worth reading, so **the headings must tell a complete story on their own**: what the product is, what problem it ends, how it solves it, and proof that it works. Each heading exists to convince the visitor that the paragraph underneath is worth reading. A heading that only makes sense after you read the body has failed.

**2. Write unique headlines.** Ask whether you could paste this headline onto a competitor's page. If you could, it's weak. **Never write "Save time" or "Save money"**, or any other claim every product in the category could make. Describe what saving that time or money looks and feels like for *this* product's customers, and what it unlocks for them. Don't write "Save hours on bookkeeping". Write "Close **March** in **six hours** and spend close week on **clients**".

## Ground rules

- **Never invent proof.** Customer quotes, names, titles, logos, review scores, user counts and statistics must come from the user or from the repo. Where they're missing, use a visible bracketed placeholder that says what's needed: `[QUOTE: finance lead confirming close takes a day]`. Never fill in something plausible-looking.
- **Write the copy before the markup.** Copy decides the page. Get it into the brief first, then build.
- **Use the project's design system.** The wireframe's greys, blue and coral only stand in for surfaces. Map them onto the project's tokens (see Step 4). Use the template's values only when the project has none.
- **One primary action.** Every CTA and the founder's invitation point to the same destination.

## Step 1: Gather what exists

Before asking anything, read what the repo and the user have already provided:

- **Product facts:** README, docs, the existing home page, pricing page, `package.json`/app metadata, onboarding screens, changelog. Pull out the category, audience, core ability and the real feature list.
- **Proof:** testimonial data, case studies, review-site links, `public/` logos, press pages, metrics already published on the site.
- **Founder:** an about page, a team page, a blog post with the origin story.
- **Stack:** the framework, styling approach (Tailwind, CSS modules, CSS-in-JS, plain CSS), component library, existing `Button`/`Section`/`Container` components, the font setup and color tokens, where routes live, and how content is stored (MDX, CMS, JSON, inline).

## Step 2: Ask once for the gaps

If key inputs are still missing, ask for them in **one** `AskUserQuestion` call or one short list. Never drip questions out one at a time. What matters most, in this order:

1. The audience and the one ability that matters most to them
2. The primary CTA and where it goes
3. Real customer quotes (one proving the hero claim, plus any that prove a specific bucket), logos and review scores
4. The founder's story, or permission to leave it as a placeholder for them to fill in
5. Which page: replace the home page, or add a new route (and what path)

If the user said to go ahead without input, don't ask. Use placeholders for missing proof and build.

## Step 3: Write the copy brief

Fill in `references/copy-brief.md` and save it in the project. The default is `landing-page-copy.md` next to the page, or wherever the project keeps content. Work through the sections in order, following the formulas in `references/sections.md`:

1. Draft 3–5 hero headlines, each from a different formula in `references/formulas.md`, mixing product-led, outcome-led and pain-led. Keep the most specific one.
2. Group every feature into **exactly three buckets**, each delivering one capability. Then write the three problems so that problem *N* is the pain bucket *N* fixes. Pick a pain point headline formula that those three cards can answer.
3. Assign quotes. The hero quote is required. Use the bucket 1 and bucket 2 quotes only if a real quote proves that bucket's claim, and otherwise mark the slot `omitted`. Match each quote to the claim it follows.
4. Draft the founder letter in its eight beats, in the first person, putting the key phrases in **bold**.
5. Tag the source of every proof item and list the open placeholders at the bottom.
6. Run both principle tests on the **Headline story** in the brief. That's every kicker and headline (hero, pain points, three buckets) and every quote, listed in page order with no body copy.
   - **Skim test:** read only that list. Does it tell the whole story by itself, and would a skimmer know what the product is, who it's for and why it's better? If not, rewrite the headline that breaks the story, not the body.
   - **Competitor test:** for each headline, name the closest competitor and check whether the headline would still be true on their page. If it would, make it specific: use this audience, this task, this outcome, a number, a feature only this product has. Remove "save time", "save money", "all-in-one", "powerful", "seamless", "streamline" and the like.

Show the user the brief, headline options included, before building, unless they said to go ahead without input.

## Step 4: Build

Port `assets/template.html` into the project's stack:

- **Components:** one per section type: `Hero`, `LogoBar`, `Quote`, `PainPoints`, `FeatureBucket` (props: `number`, `visualSide`, optional `quote` rendered after it), `Founder`. Reuse the project's existing `Button`, container and heading components. Don't make new ones that duplicate them.
- **Content:** keep all copy in one typed content object or content file built from the brief. Components take content as props. Mark headline highlights with a small, explicit convention (for example `"The **ledger** that…"` parsed into `<span class="hl">`, or an array of segments), not with HTML strings.
- **Tokens:** map the wireframe's roles onto the project's tokens:

  | Role | Wireframe | Use the project's |
  | --- | --- | --- |
  | light surface (hero, buckets) | light grey | page background |
  | muted surface (founder) | mid grey | secondary/muted background |
  | dark surface (pain points), cards | near-black, dark grey | inverse/dark background and a raised step above it |
  | accent (highlights, kickers, quote bands) | blue | brand primary |
  | accent on dark | light blue | a lighter tint of the primary |
  | CTA | coral | the primary button style |
  | display / body fonts | Poppins / Inter | the project's heading and body fonts |

- **Semantics:** exactly one `h1` (the hero headline), and an `h2` for the pain points and for each bucket. Use `figure`/`blockquote`/`figcaption` for quotes and `ul` for checks, logos and problem cards. Decorative icons and numerals get `aria-hidden`, and logos get `alt` with the company name.
- **Responsive:** as in the template. Below about 820px everything is one column, every bucket shows its text before its visual, logos sit in a 3-column grid, the problem cards stack, and the founder photo becomes a small avatar above the letter.
- **Images:** product screenshots for the hero and bucket visuals when they exist. Size them explicitly, lazy-load everything below the hero, and give the hero image priority (`fetchpriority="high"` or the framework's equivalent).
- **Metadata:** set the page `<title>` and meta description from the hero: "[Product]: [ability] for [audience]".

## Step 5: Verify

Run the dev server and look at the real page. Use Playwright screenshots, full page, at **390px and 1280px** wide. Read them and check:

- The sections appear in order, with the visuals on the left, right and left for buckets 1–3. Where an optional quote was left out, the two buckets next to each other aren't separated by a double gap. The template collapses the second bucket's top padding.
- Highlights cover only the formula's slot words, and are readable on dark surfaces.
- The contrast of white text on the accent band and of the accent-on-dark text is at least 4.5:1 (3:1 for the large quote text). If it fails, darken the band or lighten the tint.
- There's no horizontal scroll at 320px wide.
- Every CTA and the founder invitation link to the same destination.
- **Skim test on the real page:** pull every `h1`/`h2`, kicker and quote from the rendered DOM in order, and read them as one list. It should match the Headline story in the brief and stand on its own.
- Nothing invented. Search the rendered text for every proof claim and trace it back to its source in the brief.

## Report

Tell the user:

- The route and files created, and where the copy brief lives.
- The headline options with the formula behind each one, and which you used.
- The headline story: every headline in order, so the user can do the skim test themselves. Also list any headline that only partly passes the competitor test, and the specific detail that would fix it.
- How the features were grouped into the three buckets, and which problem maps to each.
- **Every open placeholder**: which quote, logo, review, photo or founder beat is still needed and where it goes.
- Which optional bucket quotes were included or left out.
- Any deviation from the format and why.
