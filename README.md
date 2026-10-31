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
| [optimize-web-fonts](optimize-web-fonts/SKILL.md) | Makes self-hosted web fonts load faster without changing how anything renders. It audits exactly which characters, weights, axis values and OpenType features the site uses, then subsets and instances each font and splits it into a preloaded core file plus an extended file behind `unicode-range`. The hand-run script's output gets committed. Chromium and WebKit pixel diffs against a baseline prove the result. Includes tested scripts for the audit, the subsetting and the diffs. |
| [seamless-mobile-safari](seamless-mobile-safari/SKILL.md) | Makes the areas behind iOS Safari's status bar and bottom toolbar match the page's top and bottom colors, including fixed backgrounds whose colors change as you scroll. It uses thin fixed edge strips, which Safari samples, kept in sync with the `html`/`body` backgrounds and `theme-color`. Based on Josh Puckett's [Seamless Backgrounds on Mobile Safari](https://joshpuckett.me/seamless-mobile-safari), with notes from WebKit's source on how Safari picks the colors. |
| [typography](typography/SKILL.md) | Professional typography rules, based on Butterick's *Practical Typography*, for anything with formatted text: web pages, documents, slides, resumes, emails. Covers font choice, spacing, layout and typographic details, with references for elements, fonts and layout. |
