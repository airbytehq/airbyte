# source-tiktok-marketing: Unique Connector Behaviors

This document describes the biggest non-obvious gotchas in `source-tiktok-marketing` that deviate from
standard declarative connector patterns. Read this before making changes to the connector.

---

## 1. Dynamic Sandbox vs Production Endpoint Selection

The connector dynamically selects between two completely different API base URLs based on the
authentication type in the config:
- **Sandbox:** `https://sandbox-ads.tiktok.com/open_api/v1.3/`
- **Production:** `https://business-api.tiktok.com/open_api/v1.3/`

This is evaluated via a Jinja expression in the `url_base`:
`"sandbox-ads" if config.get('credentials', {}).get('auth_type', "") == "sandbox_access_token" else "business-api"`.

**Why this matters:** The sandbox and production APIs have different data availability and rate limits.
When using a sandbox account, it is impossible to retrieve advertiser IDs via the API (the
`oauth2/advertiser/get/` endpoint does not work), which is why the config allows specifying an
`advertiser_id` directly. If you test changes against a sandbox account, be aware that some streams may
behave differently or return no data compared to production.

---

## 2. Dual Advertiser ID Partition Routers

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

## 3. Empty Metric Values Returned as Dash Strings

TikTok's Reporting API returns the string `"-"` (a literal dash) for metrics that have no data, rather
than returning `null` or `0`. The `TransformEmptyMetrics` custom transformation iterates over the
`metrics` object in each report record and converts any `"-"` values to `null`.

**Why this matters:** Without this transformation, downstream schemas expecting numeric types for
metrics like `spend`, `clicks`, and `impressions` would receive string values, causing type errors in
destinations. Every report stream (daily, hourly, lifetime, audience, by-country) applies this
transformation. If you add a new report stream, you must include the `TransformEmptyMetrics`
transformation or the stream will emit invalid metric types.

---

## 4. Rate Limit Detection via Response Body Code

TikTok's API does not use standard HTTP 429 status codes for rate limiting. Instead, it returns HTTP
200 with a `code` field in the JSON response body set to `40100`. The error handler uses a predicate
(`response.get('code') == 40100`) to detect rate limiting, and a separate predicate
(`response.get('code') != 0`) to detect general API errors.

**Why this matters:** Standard HTTP status code-based rate limit detection will not work with TikTok's
API. If you modify the error handler, make sure the response body code checks remain intact. The error
message also specifically warns about concurrent connections with the same credentials, as TikTok's
rate limits are per-access-token.

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

## 6. Sandbox Account Rate Limit and Credential Restriction

The TikTok Sandbox account has a rate limit of 10 requests per second. If you run CATs in CI while simultaneously testing locally with the same credentials, you will exceed this limit and the credentials may be temporarily restricted — preventing **all** requests from succeeding. The restriction appears to last a couple of hours, and there is evidence that continued request attempts during the restriction period extend the lockout duration. There is no official TikTok documentation on this restriction behavior or its exact duration.

**Why this matters:** Unlike most API rate limits that simply queue or retry, exceeding TikTok's sandbox rate limit can completely lock out the credentials for hours. Never run CI tests and local tests concurrently against the sandbox account. If you experience sudden 100% request failures with sandbox credentials, stop all requests and wait before retrying.
