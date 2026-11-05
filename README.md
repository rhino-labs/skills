# Skills

Agent skills for front-end and design work. Each folder is one skill: a `SKILL.md` with instructions, plus any `references/` and `scripts/` it uses.

## Install

```bash
npx skills add rhino-labs/skills                          # pick from the list
npx skills add rhino-labs/skills -s optimize-web-fonts    # one skill
npx skills add rhino-labs/skills -g -s '*'                # all of them, globally
```

## Skills

| Skill | What it does |
| --- | --- |
| [favicon](favicon/SKILL.md) | Generates a full favicon set (`favicon.ico`, PNGs at 96, 180, 192 and 512, `site.webmanifest`) from one source image with ImageMagick. It then detects the framework (Next.js, Astro, SvelteKit, Rails, plain HTML…) and registers the icons the way that framework expects. |
| [gsc-long-queries](gsc-long-queries/SKILL.md) | Finds long conversational Google queries (8+ words) that already hit a site in Search Console. In Performance → Search results, filter Query with Ace Cream's regex `^(?:\S+\s+){7,}\S+$`, keep the natural-language and product-intent questions, and map each one to the landing page. The deliverable is a ranked list (query, page, impressions, clicks, CTR, position) plus a few concrete next steps, from the UI or the Search Analytics API, including a cross-site list when several properties are named. It reports only numbers that came back, and it doesn't invent keywords. |
| [landing-page](landing-page/SKILL.md) | Writes and builds a product landing page in a fixed ten-section format. The sections are a hero (a product + ability + audience headline, feature checks, CTA with a risk reducer, review badges), a logo bar, three pain points, three feature buckets (with optional customer quotes proving each one), and a founder letter. Copy goes into a brief first. The headlines come from proven formulas and must pass two tests: read alone they tell the whole story, and no competitor could paste them onto their own page. Then the page is built in the project's stack and tokens. It never invents quotes, logos or stats. Includes a static reference template. |
| [optimize-web-fonts](optimize-web-fonts/SKILL.md) | Makes self-hosted web fonts load faster without changing how anything renders. It audits exactly which characters, weights, axis values and OpenType features the site uses, then subsets and instances each font and splits it into a preloaded core file plus an extended file behind `unicode-range`. The hand-run script's output gets committed. Chromium and WebKit pixel diffs against a baseline prove the result. Includes tested scripts for the audit, the subsetting and the diffs. |
| [performance-optimization](performance-optimization/SKILL.md) | Finds and fixes common back-end and front-end performance waste with small, easy-to-review diffs. It scans hot paths for sequential awaits that don't depend on each other, whole-row fetches that only read a couple of fields, needless `new URL()` parsing, regexes compiled inside functions and loops, and single keys read out of large jsonb columns. SQL review looks for missing or weak indexes (`EXPLAIN`, composite and partial indexes, concurrent migrations) and unused ones to drop. Front-end work covers fetching order, caching and profiling. Each change keeps behavior the same and is reported with the file, the change and the measured effect. |
| [seamless-mobile-safari](seamless-mobile-safari/SKILL.md) | Makes the areas behind iOS Safari's status bar and bottom toolbar match the page's top and bottom colors, including fixed backgrounds whose colors change as you scroll. It uses thin fixed edge strips, which Safari samples, kept in sync with the `html`/`body` backgrounds and `theme-color`. Based on Josh Puckett's [Seamless Backgrounds on Mobile Safari](https://joshpuckett.me/seamless-mobile-safari), with notes from WebKit's source on how Safari picks the colors. |
| [typography](typography/SKILL.md) | Professional typography rules, based on Butterick's *Practical Typography*, for anything with formatted text: web pages, documents, slides, resumes, emails. Covers font choice, spacing, layout and typographic details, with references for elements, fonts and layout. |
