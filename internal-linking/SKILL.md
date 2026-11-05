---
name: internal-linking
description: Find and add internal links that help a reader reach the next useful page, using pages the site already has. Use when the user wants to improve internal links, connect blog posts to product or money pages, fix orphans, support pages ranking around positions 11–20, rewrite anchors, or run an internal-link pass with page content, current links, and Search Console data. Not for buying backlinks or inventing fake related posts.
---

# Internal linking

## Overview

You can improve rankings and product visits with pages the site already has. Internal links help people and Google find the next useful page.

Give the pass three inputs: page content, the links already on those pages, and Search Console data. Start at S tier. For every change, name the exact source paragraph, the destination URL, and the sentence to edit.

Each section below is one scan. Run S tier before A, and A before B. A link earns its place only when the next page helps the reader do something the current paragraph raises.

## Agent workflow

Stay read-only until the user asks you to implement. Analysis produces a reviewable list. Implementation produces small content diffs.

1. **Gather inputs before proposing links.**
   - A sitemap or CMS URL list of published pages.
   - A crawl, or an existing crawl export. If you run one, fetch HTML and record status, canonical, and indexability.
   - Current on-page links taken from the content itself (article body, product copy, support answers), separate from nav and footer templates.
   - Search Console query and page data: position, impressions, clicks, and the ranking URL. Keep rows around positions 11–20, and pages with high impressions.
   - If a source is missing, say so. Do content and orphan work from the repo without Search Console. Do not invent positions, impressions, or queries. Do not write a sentence you have not read on the source page.

2. **Prioritize S, then A, then B.** Finish the S-tier opportunities that have a real destination before you spend the pass on footer labels or pagination. Skip a tactic when the site has no pages of that kind.

3. **For each proposed change, output all of the following.**
   - **Source URL**
   - **Paragraph:** the exact sentence or short passage on the source page, quoted from the page
   - **Destination URL:** a page that already exists
   - **Edit:** the full new or edited sentence, with the anchor in words a reader would say
   - **Tier:** S, A, or B, and the tactic name
   - **Why:** what the reader can do on the destination that this paragraph set up

4. **Ship small batches.** When the user asks you to implement, edit the content source (Markdown, MDX, HTML, or the CMS export in the repo) and open reviewable diffs. One source page, or one destination, per batch is enough. Do not dump every candidate into one change.

5. **Use only what exists.** Do not invent quotes, case studies, product pages, or related posts. Do not keyword-stuff anchors. If the right destination does not exist, say so and leave the sentence unchanged.

6. **Stop at the list until the user asks for edits.** Then change copy and `href`s. Do not publish, deploy, or submit URLs to Search Console unless the user asks.

## S tier

### Link articles to money pages

Pick the product each topic supports before you add links, so every article link has a destination that matches the job the reader is doing.

- Link a tutorial to the feature that completes the task, so the reader can try the thing the tutorial just explained.
- Send integration questions to the matching integration page, so the reader can see how that connection works.
- Link a buying guide to the offer that matches the choice the guide is helping the reader make.
- Connect related product pages where a reader needs to see how the products work together.
- Link a product claim to a case study that documents that claim, so a buyer can inspect the proof. If no such case study exists, leave the claim unlinked and say what is missing.

### Link guides and support posts

Link both ways when both directions help, and give each direction its own reason. A link up to the overview and a link down to a step are different jobs.

- Link a broad guide to the detailed answer that finishes a step.
- Link the detailed post back to the guide when the reader needs the rest of the process.
- Connect related support posts so the next question the reader will have has an answer.
- Link related guides where finishing one task leads into the next.
- Cross blog categories when the next answer lives in another category and still fits the task. Skip the cross-link when the tasks only share a keyword.

### Link to neglected pages

- Compare crawl URLs with the sitemap or CMS URL list. A published, indexable URL the crawl never reached is an orphan candidate.
- Add incoming links from pages a reader of that orphan would already be on. An orphan with no honest source stays on the list as a content problem.
- When you count links, separate template links (menus, footers, related blocks) and same-page jumps from links inside article or product copy. Use the in-content count to judge what is neglected.
- Review the pages that already receive the most in-content links and look for an important answer those pages never mention.
- Pick a neglected priority URL and support it from several relevant pages, each with its own sentence. Do not paste one sentence onto every page.

### Help pages near page one

- From Search Console, take queries sitting around positions 11–20.
- Confirm the ranking URL is the page that answers that query. Send links to that URL. If a different page owns the answer, say so instead of reinforcing the wrong URL.
- Prefer queries that keep earning impressions over a one-off row.
- Link from established, related articles into those URLs. Established means the source already earns attention: backlinks, a popular tutorial, cited research, or a relevant section of the homepage. The source still has to be about the same task.

## A tier

### Find useful links in older content

- Search the site for the destination's topic, including the tasks around it. Exact-keyword matches are the start of the search.
- Read the paragraph around each mention. Add a link only where that paragraph is the moment the reader needs the other page.
- When a new answer goes live, add links from older posts that still send people to a weaker or older recommendation. Replace the outdated recommendation with the current answer. Leave a historical mention alone when it is quoting what was true at the time.

### Write anchors people understand

- Name the destination's subject. "Click here", "this article", and a bare URL do not tell the reader what will open.
- When the page is a specific task, put that task in the anchor.
- The anchor has to match what the destination contains. If the page does not do the thing the anchor promises, change the anchor or pick another page.
- Let each sentence produce its own anchor. Vary the wording the way the sentences vary. Do not rotate a keyword list.
- Keep navigation labels consistent for the same destination, so a reader who learned the name in the menu still recognizes it.
- When the link is an image, write alt text that describes the destination.

### Put links where readers need the answer

- Place the link beside the decision it helps with.
- Put a useful link in the first explanation of that point, where the reader is still on the question.
- In the sentence, say what the next page helps the reader do.
- When two destinations compete, give them separate sentences so each choice is visible.
- Keep link styling visible against the text, and leave enough space that a thumb can hit the link on a phone. Call this out as a template change, separate from copy edits.

### Use pages that already earn attention

Prefer these as sources when they are about the destination:

- Pages that already have backlinks, as the source of a new link.
- Popular tutorials, linked onward to the next useful guide.
- Research or data pages the site cites, linked to the product that research supports.
- A relevant section of the homepage, when the priority page belongs in that section.

Leave the homepage alone when the priority page does not fit the section a visitor is scanning.

### Connect buying decisions

Follow the question the reader is in:

- Comparison pages link to current pricing, so the budget question has a current answer.
- Alternatives pages link to the migration or switching guide.
- Feature pages link to the setup guide for that feature.
- Use-case articles link to the service or product page for that use case.
- Proof pages (case studies, results) link to the offer they document, once the proof has made the case.

Use the live pricing, migration, setup, and offer URLs. When a page has moved, point at the current one.

## B tier

### Make important pages easy to reach

- Put main products in the navigation.
- Put useful products and guides in the footer so those routes stay available after the article ends.
- Link each category page to the products in that category.
- Link a deep page from its nearest topic hub so the path is short.
- In related-content blocks, choose the next task. A reader who just finished a step needs the following step.

### Fix broken and indirect links

- Replace a broken destination with the live page that answers the same question. If nothing live answers it, remove the link and say so.
- Point links at the final URL, skipping a redirect you already know how to resolve.
- Use the preferred version of a page: the host, path, and trailing slash the site declares as canonical.
- After two articles are merged, point old links at the surviving page.
- Use real links with `href` destinations. A control that only navigates in JavaScript is not a link a crawler can follow.
- When a template change dropped links, restore the ones that still point at a useful page.

### Keep large collections connected

- Give a large or programmatic collection a category hub a person can browse.
- Connect related location or use-case pages when a visitor would compare those options.
- Paginate long archives with crawlable links (`a href` to the next page). An infinite scroll with no linked page leaves older URLs unreachable.

### Improve links readers skip

Use scroll and click data when the user has it (analytics, a heatmap, clicks per page view). Without that data, do not claim a link is skipped.

- Move a useful link above the point where readers drop off.
- Rewrite a link people see and do not click so the sentence says what answer they will get.
- Replace a destination that does not answer the question the paragraph raises.
- When two wordings or placements exist, keep the one with the higher clicks per view, and cite the numbers you used.

## Example

A template that helps someone write a welcome email links to the full welcome-sequence guide, because the reader who has one email needs the rest of the sequence. The guide links to the software that sends it, because the reader who has the sequence needs to send it. The template also links straight to that product when the paragraph is about sending the first email.

Apply the same chain on any topic: the narrow asset, the fuller guide, and the product that does the job. Add the direct product link on the narrow page in the sentence where it helps the reader act.

## Sources

Tactics ranked by Borja ([@borjafat](https://x.com/borjafat)) in [INTERNAL LINK MAXXING with Claude](https://x.com/borjafat/status/2117962517016170502). The article mentions Distribb for automation; this skill works without it.
