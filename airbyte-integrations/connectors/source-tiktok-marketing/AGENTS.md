> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-tiktok-marketing: Unique Connector Behaviors

This document describes the biggest non-obvious gotchas in `source-tiktok-marketing` that deviate from
standard declarative connector patterns. Read this before making changes to the connector.

---

The connector uses the production API at `https://business-api.tiktok.com/open_api/v1.3/`.
Live tests use production credentials; TikTok's retired sandbox authentication is not supported.

## 1. Dual Advertiser ID Partition Routers

The connector uses two custom partition routers that handle advertiser IDs differently depending on
whether the ID is provided in the config or fetched from the API:

- **`SingleAdvertiserIdPerPartition`:** Used by most streams. If `advertiser_id` is in the config,
  yields a single partition with that ID and skips the parent stream entirely. Otherwise, yields one
  partition per advertiser ID from the `advertiser_ids` parent stream.
- **`MultipleAdvertiserIdsPerPartition`:** Used only by the `advertisers` stream. Batches up to 100
  advertiser IDs into a single JSON array partition (e.g., `'["id1", "id2", ...]'`), because TikTok's
  advertiser info endpoint accepts multiple IDs per request.

Both routers check multiple config paths in priority order (`credentials.advertiser_id` then
`environment.advertiser_id`).

**Why this matters:** The `advertisers` stream sends advertiser IDs as a JSON array string in the
request parameter, not as individual values. If you change how advertiser IDs are partitioned, the
`advertisers` stream needs the batched format while all other streams need individual IDs. Mixing these
up will cause either missing data (single ID sent where array expected) or API errors (array sent where
single ID expected).

---

## 2. Empty Metric Values Returned as Dash Strings

TikTok's Reporting API returns the string `"-"` (a literal dash) for metrics that have no data, rather
than returning `null` or `0`. The `TransformEmptyMetrics` custom transformation iterates over the
`metrics` object in each report record and converts any `"-"` values to `null`.

**Why this matters:** Without this transformation, downstream schemas expecting numeric types for
metrics like `spend`, `clicks`, and `impressions` would receive string values, causing type errors in
destinations. Every report stream (daily, hourly, lifetime, audience, by-country) applies this
transformation. If you add a new report stream, you must include the `TransformEmptyMetrics`
transformation or the stream will emit invalid metric types.

---

## 3. Rate Limit Detection via Response Body Code

TikTok's API does not use standard HTTP 429 status codes for rate limiting. Instead, it returns HTTP
200 with a `code` field in the JSON response body set to `40100` or `40016` (app-level limits) or `40133`
(advertiser-level limit). The error handler uses a predicate
(`response.get('code') in [40016, 40100, 40133]`) to detect rate limiting, and separate predicates
(`response.get('code') == 50000`, `response.get('code') == 51041`,
`response.get('code') == 51004`, `response.get('code') == 51002`, `response.get('code') == 51001`, and
`response.get('code') == 51043`) retry transient server-side errors, while
(`response.get('code') != 0`) detects general API errors.

**Why this matters:** Standard HTTP status code-based rate limit detection will not work with TikTok's
API. If you modify the error handler, make sure the response body code checks remain intact. The error
message also specifically warns about concurrent connections with the same credentials, as TikTok's
rate limits are per-access-token.

---

## 4. Daily Report Window Splitting (40067)

TikTok rejects a daily report request that is too large with HTTP 200 and body `code` 40067 ("Your query
is too large, please reduce the query size..."). `report_daily_error_handler` maps it to
`SPLIT_REQUEST_WINDOW`, so the CDK re-reads that advertiser's rejected window as two halves, recursively.

- The 40067 filter is predicate-only on purpose: the error arrives with HTTP 200, and `HttpResponseFilter`
  ORs its conditions, so adding `http_codes` would split every page.
- All 19 `*_daily` streams get it through `base_report_retriever` and `audience_base_report_retriever`,
  which share `report_daily_request_window_splitting`.
- The floor is one day, from `cursor_granularity: P1D` on `report_daily_incremental_sync` (no
  `min_split_window`). A single day that is still rejected fails the stream with a `transient_error`
  (CDK behavior), followed by the block's `failure_message`.
- Any retriever that `$ref`s `report_daily_error_handler` must also `$ref`
  `report_daily_request_window_splitting`, or the manifest fails to load (the CDK rejects a
  `SPLIT_REQUEST_WINDOW` filter on a retriever without `request_window_splitting`).
- Hourly retrievers must not get it: hourly requests always cover one day, so halving the window would
  repeat the same request.

**Why this matters:** A new daily report retriever or a copied error handler that misses one of these
rules either fails to load or fails on 40067 instead of splitting.

---

## 5. Smart+ Ads Missing modify_time Filter

The `ads` stream includes a `RecordFilter` that drops records where `modify_time` is `None`. This is
specifically to handle TikTok's Smart+ Ad records, which can be returned by the API without a
`modify_time` value. Since the stream uses `modify_time` as its incremental cursor, records without
this field would cause cursor comparison failures.

**Why this matters:** This filter silently drops valid ad records from the sync output. If a user
reports missing ads data, Smart+ ads without `modify_time` values are the likely cause. This is a known
trade-off to maintain incremental sync reliability.

---

## Incremental Stream Considerations

The TikTok Marketing API supports date-based filtering on report endpoints. The connector uses Python custom components referenced from the manifest.

**Connector type:** Python custom components (hybrid manifest + Python)

**Analysis status:** Streams are Python-defined via custom components. Full stream-by-stream analysis requires Python code review.

### Future incremental stream candidates

- **All streams deferred for Python code review:** This connector defines its streams in Python code rather than declarative manifest YAML. A full stream-by-stream incremental analysis table (per the standard CONTRIBUTING.md schema) should be added by a future agent after reviewing the Python stream definitions, their `cursor_field` properties, and the API endpoints they call.
