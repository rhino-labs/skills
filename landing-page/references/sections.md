# Sections: purpose, copy formula and layout

The page has up to ten sections in a fixed order. Six section types are used, and the quote and feature types repeat:

| # | Section | Type | Surface |
| --- | --- | --- | --- |
| 1 | Hero | `Hero` | light |
| 2 | Logo bar | `LogoBar` | light, continues the hero |
| 3 | Quote: proves the hero headline | `Quote` | accent |
| 4 | Three pain points | `PainPoints` | dark |
| 5 | Feature bucket 1, visual on the left | `FeatureBucket` | light |
| 6 | Quote: proves bucket 1 *(optional)* | `Quote` | accent |
| 7 | Feature bucket 2, visual on the right | `FeatureBucket` | light |
| 8 | Quote: proves bucket 2 *(optional)* | `Quote` | accent |
| 9 | Feature bucket 3, visual on the left | `FeatureBucket` | light |
| 10 | Founder letter | `Founder` | muted |

The page argues one thing at a time. Each light section makes a claim, and the accent quote right after it proves that claim in a customer's words. Bucket 3 has no quote after it, because the founder letter follows straight away.

Quotes 6 and 8 are optional. Include one only when a real customer quote proves that bucket's specific claim. Without one, the buckets sit next to each other, which still reads well because the visual swaps sides. A generic quote in that slot is worse than none. Quote 3 is always included.

Keep this order. Don't add sections (pricing, FAQ, a final CTA band) unless the user asks. If they do, put them after the founder letter.

---

## 1. Hero

**Job:** Say what the product is, what it lets you do, and who it's for, all before the reader scrolls.

| Element | Copy rule |
| --- | --- |
| Kicker | The product category, in a few words, uppercase. The term the audience would search for: "Bookkeeping software", "Applicant tracking". |
| Headline (`h1`) | Pick one of the hero formulas in `formulas.md`. The default is **The [product] that enables [this ability] for [this audience].** Highlight the words that fill the slots. If the formula leaves out the product, ability or audience, the kicker and explainer must cover it. |
| Explainer | 1–2 sentences. Name the key features that give the product its capabilities, plus the benefits those deliver. |
| Feature checks | Three short key product features, each with a check icon. Each one is a fragment, at most about 6 words. |
| Primary CTA | Verb first, and says what happens: "Start free trial", "Book a demo". This is the same action as every other CTA on the page. |
| Risk reducer | One small line under the button that takes away the reason not to click: "No credit card required", "Free for 14 days, cancel anytime", "Setup in 5 minutes". |
| Reviews | Three review badges side by side: stars, score, and source (G2, Capterra, App Store, Product Hunt, Trustpilot). Use real ratings only. With fewer than three, show the ones you have. With none, leave out the row rather than adding a placeholder. |
| Visual | On the right: a product screenshot, or an illustration of the outcome. The wireframe's rocket stands in for this. |

Example:

> **Kicker:** Bookkeeping software
> **Headline:** The **ledger** that closes your **books in a day** for **growing agencies**
> **Explainer:** Bank feeds, automatic categorization and one-click reconciliation do the monthly busywork, so your team spends close week on clients and not spreadsheets.
> **Checks:** Live bank feeds · Rules that learn your categories · Reconcile in one click
> **CTA:** Start free trial · *No credit card required*

**Layout:** Two columns, about 55/45, with the text on the left. On mobile, stack the text first and the visual after it. The review badges wrap onto two lines if they need to.

## 2. Logo bar

**Job:** Show that companies the reader recognizes already use the product.

- Lead-in: one centered line framed around the benefit: "Teams at these companies close their books faster". The wireframe's line is "These brands enjoy our benefits".
- 4–6 customer logos, grayscale at equal visual weight, spaced evenly. Use real customers only, with permission. Without logos, drop the section and don't fake it.

**Layout:** One row on desktop. A 3-column grid or two rows on mobile.

## 3, 6, 8. Quote

**Job:** Prove the claim made in the headline just before it.

- The quote is short: 1–2 sentences, about 25 words at most. It repeats the previous headline's promise with a specific result: "We closed March in six hours. It used to take us a week."
- Attribution: name, position, company. Add a headshot if you have one.
- Choose a quote for each slot by matching it to the claim it follows. Quote 3 proves the hero, quote 6 proves bucket 1, and quote 8 proves bucket 2. Never reuse a quote. Quote 3 is required, with a placeholder if it's missing. Leave out quotes 6 and 8 when no quote proves that bucket's claim.

**Layout:** A full-width band on the accent color. Large, bold, centered text in white, with a maximum width of about 32ch. The attribution sits under the quote in a smaller size.

## 4. Pain points

**Job:** Name the problem the reader already feels before showing the fix. This makes the features that follow read as answers.

| Element | Copy rule |
| --- | --- |
| Kicker | "The big industry problem", or the problem named in a few words. |
| Headline (`h2`) | Pick one of the pain point formulas in `formulas.md`. It sums up the industry problem that the three problems below add up to. Highlight the slot words. "**Agency owners** experience **a lost week every month** when they **close the books**" |
| 3 cards | Each card has an icon and a "Problem N" label, then the problem in **bold** followed by one or two sentences in the lighter accent color describing the painful effects. Write each problem in the reader's own words. |

The three problems should map one-to-one onto the three feature buckets, in the same order. Problem 1 is solved by bucket 1, and so on.

**Layout:** A dark surface with the text centered above three equal cards. The cards are a slightly lighter dark color with rounded corners. On mobile the cards stack.

## 5, 7, 9. Feature bucket

**Job:** Turn one problem into one capability, and back it with concrete features.

A *bucket* is a group of related features that together deliver one capability. Group the product's features into exactly three buckets, matching the three problems.

| Element | Copy rule |
| --- | --- |
| Kicker | `N. Bucket name`, for example "1. Automation" |
| Headline (`h2`) | **Gain [this capability] with [these features].** Highlight the capability and the feature group. "Get **close week back** with **automatic categorization**" |
| Body | 2–3 sentences. Describe the benefits of the bucket, and say why this is a better approach than the way the competition, or the status quo, does it. |
| Feature checks | Three features in the bucket, each with a check icon. |
| Visual | A screenshot or illustration of that capability. The wireframe's large numeral (1, 2, 3) is a placeholder for it. If no visual exists, a large outlined numeral is acceptable. |

**Layout:** Two columns. The visual is on the left for buckets 1 and 3, and on the right for bucket 2. When two buckets are adjacent because a quote was left out, drop the second one's top padding so the gap matches a single section. On mobile every bucket stacks text first and then the visual, so the order doesn't jump around.

## 10. Founder letter

**Job:** Put a person behind the product and close the argument with a story.

A personal letter written in the first person, in short paragraphs, in this order:

1. **Introduce yourself.**
2. **Your background**, to build credibility and a connection with the reader.
3. **The problem you experienced**, and how it affected you. Use it to show the problem is real and to build empathy.
4. **Your breakthrough realization.** Highlight key phrases in **bold**, here and in the rest of the letter.
5. **Wins** that you and early customers have had with the product.
6. **Your vision** for the future.
7. **Invite them to try the product.** Link this sentence to the primary CTA's destination.
8. **Sign-off:** name, title, and a signature or headshot.

**Layout:** The letter is on the left with a maximum width of about 60ch, on a muted surface a step darker than the light sections. The founder's photo is on the right. On mobile the photo goes above the letter at a small size.

---

## Copy rules for the whole page

- **Headlines tell the whole story.** Someone who reads only the kickers, headlines and quotes, in order, should come away knowing what the product is, who it's for, what problem it ends, how it works and that customers vouch for it. Each heading's job is to earn a read of the paragraph under it.
- **Headlines a competitor couldn't use.** If a headline would be just as true on a competitor's page, it's weak. Never write "Save time" or "Save money", because every B2B product claims both. Show what that saving looks and feels like for *these* customers with *this* product, and what it unlocks.
- **The reader's words, not yours.** Use the terms from customer quotes, reviews, support tickets and sales calls. Avoid internal feature names unless customers use them.
- **Specific beats impressive.** Use "Close March in six hours" and not "Blazing-fast reconciliation". Numbers, times and named outcomes.
- **One CTA.** Every button and the founder invitation go to the same place.
- **Accent highlights** go on the words that fill a formula's slots, and nothing else. Keep each slot to a short phrase. On dark surfaces, use a lighter tint of the accent that still meets contrast.
- **Never invent proof.** Quotes, names, logos, review scores, customer counts and statistics must come from the user or from the codebase. Where proof is missing, leave a visible placeholder like `[QUOTE: proves "close in a day" — from a finance lead]` and list every placeholder in the report.
