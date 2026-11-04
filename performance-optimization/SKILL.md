---
name: performance-optimization
description: Find and fix common back-end and front-end performance waste in a codebase with small, easy-to-review diffs. Covers unnecessary sequential awaits on hot paths, over-fetching whole rows, needless `new URL()` parsing, regexes compiled inside functions and loops, hot keys read out of large jsonb columns, missing or weak SQL indexes, and front-end fetching, caching and profiling. Use when the user wants faster software, asks for a performance pass, a hot-path audit, query or index review, or asks why an endpoint, page or query is slow. Not for rewriting in another language or changing product behavior.
---

# Performance Optimization

## Overview

Do less work. Each section below is one scan. Run them one at a time, keep each change small and behavior-preserving, and prefer many boring diffs over one clever rewrite.

For every scan:

1. **Find the hot paths first.** Request handlers, frequently rendered components, loops over large collections, background jobs that run often. Use traces, APM data, logs or a profiler where available.
2. **Measure before and after.** Latency, query time, rows/bytes read, CPU. Don't claim a win you didn't measure.
3. **Keep behavior identical.** Ordering, error handling and side effects must not change unless the user approves.
4. **Report** each finding with file and line, the change, and the measured effect.

## 1. Parallelize unnecessary sequential async calls

Scan all hot paths for `await`s that run one after another but don't depend on each other.

- Look for consecutive awaits where the second doesn't use the first's result, and `await` inside `for` loops over independent items.
- Replace with `Promise.all` (or `Promise.allSettled` when one failure shouldn't fail the rest; `asyncio.gather`, goroutines/errgroup, etc. in other languages).
- For loops over many items, cap concurrency (e.g. `p-limit`) so you don't overload the database or a third-party API.
- Keep sequencing where it's real: a write that must finish before a read, transactions, rate-limited APIs.

## 2. Select only the fields you need

Find every place that loads a whole row (`SELECT *`, ORM `findOne`/`find` without a field list, eager-loading whole relations) only to read a couple of fields.

- Select just the columns used (`select`, `pluck`, `only`, `attributes`, projections).
- Biggest wins: tables with large text, jsonb or blob columns; wide tables; serverless or cross-network database connections where transfer is not free.
- If the selected columns are all in an index, the query can become an index-only scan; see section 6.
- Don't break code that later reads other fields from the same object. Check usages before trimming.

## 3. Remove unnecessary `new URL()` parsing

- Find `new URL()` (and `URL.parse`, `url.parse`, `URLSearchParams` built from full URLs) in hot paths, loops and per-request middleware.
- Remove it where a plain string operation does the job (checking a prefix, reading a known path), where the value is already parsed elsewhere, or where the same URL is parsed repeatedly. Parse once and pass the result along.
- Keep it where correctness depends on real parsing: untrusted input, origin/security checks, normalization.

## 4. Compile regexes once, at module level

- Find regex literals and `new RegExp(...)` built inside functions, loops, and request handlers, especially in hot paths.
- Hoist constant patterns to module-level constants so they compile once at startup, not on every call.
- For dynamic patterns built from a small set of inputs, cache the compiled regex (a `Map` keyed by the pattern).
- Watch for global/sticky flags (`g`, `y`): a shared regex keeps `lastIndex` state between calls. Reset it or drop the flag when hoisting.

## 5. Promote hot jsonb keys to real columns

Find hot-path reads of a single key from a large jsonb (or json/text-blob) column, e.g. `data->>'status'` in a `WHERE`, `ORDER BY` or select list. Reading one key can force Postgres to detoast the whole value, and in one reported case that meant reading 20 GB+ to return a few KB.

- Add a real column for the key (or a generated column: `GENERATED ALWAYS AS (data->>'key') STORED`) and index it if it's filtered or sorted on.
- Sequence the rollout on hot tables: add the column nullable, dual-write from the application, backfill in small batches, verify, switch reads, then optionally drop the key from the jsonb. Plan for stale reads during the backfill window.
- Prefer real columns over large jsonb blobs for anything read often.

## 6. Analyze SQL queries for missing or better indexes

Review the application's queries for missing indexes or index improvements.

- Collect the queries that matter: slow query log, `pg_stat_statements` (by total time and by calls), ORM query logs, or the queries behind the hot paths found above.
- Run `EXPLAIN (ANALYZE, BUFFERS)` (or the database's equivalent) on each. Look for sequential scans on large tables, high rows-removed-by-filter, sorts and hash joins on large inputs, and big estimate vs. actual row gaps.
- Recommend indexes matching the query's `WHERE`, `JOIN` and `ORDER BY`: composite indexes with equality columns first, then range/sort columns; covering indexes (`INCLUDE`) for index-only scans; partial indexes for common filters (`WHERE deleted_at IS NULL`); expression indexes for computed lookups (e.g. `lower(email)`).
- Find indexes to improve or remove: unused (`pg_stat_user_indexes.idx_scan = 0`), duplicate, or redundant prefixes of other indexes. Every index costs writes and storage.
- Check foreign keys have indexes when they're joined on or deleted through.
- Create indexes without locking hot tables (`CREATE INDEX CONCURRENTLY` in Postgres) and ship them as migrations. Re-run `EXPLAIN` to confirm the planner uses them.

## 7. Front-end fetching, caching and profiling

- **Profile first.** Record a flame graph (browser DevTools Performance, Node `--cpu-prof`, `0x`, py-spy, etc.) and clean up the widest frames.
- **Prioritize what the user sees first.** Fetch data for above-the-fold components first; lazy-load the rest. Start independent requests in parallel instead of waterfalls between parent and child components.
- **Fetch faster instead of hiding it.** Prefer removing slow fetches over adding more loading skeletons.
- **Check the database query behind each slow API call** (sections 2, 5 and 6).
- **Look for caching opportunities:** HTTP caching headers, CDN, memoized computations, request deduplication, and application caches for expensive, rarely changing data. Define invalidation before adding a cache.
- **Make async whatever can be:** move non-critical work (emails, analytics, webhooks) off the request path into background jobs.

## Sources

Ideas from an X thread by Dylan Garcia ([@_dylanga](https://x.com/_dylanga/status/2117400205314421058)), with additions from Ryan Anderson (SQL index analysis) and replies from @lozards (front-end profiling, fetching and caching).
