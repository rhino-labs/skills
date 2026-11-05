---
name: gsc-long-queries
description: Find long conversational Google queries (8+ words) that already hit a site in Search Console, and map the ones that point at a product or page. Use when the user wants LLM-style or ChatGPT-style questions already in their search data, natural-language queries pointing at their products, or a ranked list of those queries with landing page, impressions, clicks, CTR and position. Not for inventing keywords from scratch or keyword stuffing.
---

# GSC Long Queries

## Overview

Pull the searches of 8+ words that already reach a property in Google Search Console, keep the ones that are real conversational questions, and map each one to the page that ranks. Deliver a short ranked list plus a few concrete next steps. Report only numbers the export or API returned.

Run one property at a time. Use the property the user named. If they didn't name one, list the properties you can read and ask which to run. Don't scan every property you can see.

The filter is fixed. Don't shorten it to manufacture more rows.

```
^(?:\S+\s+){7,}\S+$
```

That is 7 or more "token plus whitespace" groups, then a final token: 8 or more whitespace-separated tokens, anchored to the whole query. A token is `\S+`, so a hyphenated compound or a word with punctuation counts as one token. Judge the rows the regex returns. Don't re-tokenize them and drop matches.

## 1. Pull the long queries in Search Console

For one property:

1. Open [Google Search Console](https://search.google.com/search-console) and select the property.
2. Go to **Performance → Search results**.
3. **Add filter → Query → Custom (regex)**. Use the include / matches variant.
4. Paste `^(?:\S+\s+){7,}\S+$` with no surrounding quotes, and apply.

The table is every search of 8+ words that Google has shown for this property. The report lists at most 1,000 queries, and the export has the same cap. A full table means the property has more. Use the API in section 5 for the rest. Don't treat a full export as the whole set.

## 2. Set the date range

Use the last 28–90 days of **final** data. Search Console lags about 2–3 days, so end the range on the latest finalized date.

- A 28-day window is enough for a first look. Use up to 90 days when the property is thin or the user wants a wider set.
- The **Last 28 days** and **Last 3 months** presets are fine when they already stop before the incomplete trailing days.
- Skip period-over-period comparison unless the user asks. This is a snapshot of queries that already point at the site.

## 3. Keep the conversational ones

The regex only measures length. Read each query and keep the ones a person would type, or ask a model.

Keep:

- Questions and prompts: how, why, what, when, where, which, can I, should I, is it, does it.
- Multi-clause prompts: a condition plus a question, or two asks in one search.
- Product-intent questions: the searcher wants a tool, a feature, a comparison, or a way to do the job the product does.

Leave these out of the product list:

- Long stacks of brand, tool, and navigational words (`login`, `pricing`, `dashboard`, `admin`) with no question.
- URL-like or copy-pasted strings.
- The same keywords repeated to hit a length.

Keep non-English queries when they are conversational. `\S` is not limited to ASCII.

Rank by impressions so the stronger rows lead. Keep a low-volume question when it clearly points at the product. A short list is a real result. Don't relax the 8-word filter, and don't invent queries that were not in the export.

## 4. Map each query to its landing page

For each query you keep, record the page that earned the impressions.

- In the UI, click the query, then open **Pages**. Note the URL, impressions, clicks, CTR, and average position.
- A good match: the page's product or tool is what the question asks for.
- A wrong page: the question is about the product but lands on a tag, the blog index, a docs root, or an unrelated article.
- Cannibalization: the same query has impressions on two or more URLs. List every URL. Name the page that already answers the question as the owner, and say why.

Copy the figures from the export or the API. If a metric is missing, leave it blank and say so.

## 5. Pull the same data from the API

Use this when you have the Search Analytics API, or any connector that wraps it. Pass the same filter. Don't depend on a vendor-specific tool name, and don't hardcode a site list.

`POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query`

URL-encode `{siteUrl}`. A URL-prefix property looks like `https://www.example.com/`. A domain property looks like `sc-domain:example.com`. Use the property the user named. Read-only access is enough.

Per property:

- Search type: `web`. Leave image, video, news, and Discover for a separate request if the user asks.
- Dimensions: `query` and `page`, so each row is one query on one URL.
- Filter: dimension `query`, operator `includingRegex`, expression `^(?:\S+\s+){7,}\S+$`.
- Dates: `startDate` and `endDate` as `YYYY-MM-DD`, finalized data only. Omit `dataState`, or set it to `final`.

Paginate. `rowLimit` max is 25000. Start at `startRow` 0 and add `rowLimit` until a page returns fewer rows than you asked for.

In JSON the backslashes are escaped. In the Search Console UI they are not.

```json
{
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "dimensions": ["query", "page"],
  "type": "web",
  "dimensionFilterGroups": [
    {
      "filters": [
        {
          "dimension": "query",
          "operator": "includingRegex",
          "expression": "^(?:\\S+\\s+){7,}\\S+$"
        }
      ]
    }
  ],
  "rowLimit": 25000,
  "startRow": 0,
  "dataState": "final"
}
```

`keys[0]` is the query. `keys[1]` is the page. `ctr` is a fraction from 0 to 1; show it as a percentage rounded from that fraction. `position` is the average position. Use the returned clicks, impressions, CTR, and position.

Google withholds some queries for privacy. The rows you get are the ones Search Console returned. Say that when the property looks thin. Don't pad the gap.

## 6. Run several properties

When the user names more than one site or product, repeat sections 1–5 once per property. Don't merge properties into one API call.

Then build one cross-site list of the conversational, product-pointing rows, sorted by impressions, then clicks. Include the property on every row.

Report a thin property as thin. Don't borrow queries from another property to fill it.

## 7. Deliver the list and the next steps

Lead with a short ranked table. One row per query and page. Sort by impressions, then clicks. Columns: query, page, impressions, clicks, CTR, position. Add a property column when you ran more than one. Above the table, give the property, the date range, and that the data is finalized. State how many long queries you dropped as non-conversational, so the cut is visible.

Then give up to 3–5 next steps, each tied to a row you actually returned. Fewer when the property is thin. Don't invent steps to hit a count.

- Which page should own which question. When several URLs split one query, name the owner.
- A wrong-page match: name the page that should own it.
- An FAQ or section to add, written as the natural question people asked. One question, one place to answer it.

Write the question the way the searcher asked it. Don't produce keyword-stuffed FAQ variants (`best`, `near me`, `cheap`, or the same question rephrased into a cluster). Don't invent impressions, clicks, CTR, or position. If you couldn't read a property, say so and leave it out of the ranking.

## Constraints

- Read-only. Don't edit the site, open a content PR, or draft replacement copy unless the user asks.
- Don't post the queries or the write-up anywhere public.
- Don't invent keywords, queries, or metrics. Empty and thin properties stay in the report as thin.
- Don't add country, device, or page filters unless the user asks. The trick is the length filter alone.
- Don't change the regex to chase a bigger list.

## Sources

Oleksii / Ace Cream ([@acecreamu](https://x.com/acecreamu/status/2117614396243341586)): in Search Console, Performance → Search results, filter Query with `^(?:\S+\s+){7,}\S+$` to list every search of 8+ words — the long, specific questions people google before they reach you.
