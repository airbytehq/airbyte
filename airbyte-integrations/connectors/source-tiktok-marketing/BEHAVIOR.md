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

## 4. Semi-Incremental Sync with Client-Side Filtering

Entity streams (campaigns, ad_groups, ads, creative_assets_images, creative_assets_videos) use
`is_client_side_incremental: true`, meaning the API does not support server-side filtering by
`modify_time`. The connector fetches all records and filters them locally based on the cursor value.

TikTok's entity listing endpoints (`campaign/get/`, `adgroup/get/`, `ad/get/`) do not support a
`modified_since` or equivalent filter parameter. They only support status-based filtering.

**Why this matters:** Every incremental sync of entity streams fetches the complete dataset from the
API, regardless of cursor position. For accounts with many campaigns, ad groups, or ads, this means
sync duration and API usage do not decrease over time -- they are always proportional to the total
number of entities, not just recently modified ones.

---

## 5. Report Attribution Window Lookback

Report streams (daily and hourly) support a configurable `attribution_window` (default: 0 days) that
is applied as a `lookback_window` on the `DatetimeBasedCursor`. TikTok's ad attribution can update
conversion metrics retroactively as attribution data finalizes, meaning a report row for day X may
change values for several days after day X.

**Why this matters:** If users set `attribution_window` to a non-zero value (e.g., 7 days), the
connector will re-fetch report data for the lookback period on every sync, even if that data was
already synced. This is intentional to capture late-arriving attribution updates, but it means report
syncs will always request at least `attribution_window` days of data regardless of the cursor position.
Users must use an append-dedup sync mode in their destination to handle the re-emitted records.

---

## 6. Rate Limit Detection via Response Body Code

TikTok's API does not use standard HTTP 429 status codes for rate limiting. Instead, it returns HTTP
200 with a `code` field in the JSON response body set to `40100`. The error handler uses a predicate
(`response.get('code') == 40100`) to detect rate limiting, and a separate predicate
(`response.get('code') != 0`) to detect general API errors.

**Why this matters:** Standard HTTP status code-based rate limit detection will not work with TikTok's
API. If you modify the error handler, make sure the response body code checks remain intact. The error
message also specifically warns about concurrent connections with the same credentials, as TikTok's
rate limits are per-access-token.

---

## 7. Smart+ Ads Missing modify_time Filter

The `ads` stream includes a `RecordFilter` that drops records where `modify_time` is `None`. This is
specifically to handle TikTok's Smart+ Ad records, which can be returned by the API without a
`modify_time` value. Since the stream uses `modify_time` as its incremental cursor, records without
this field would cause cursor comparison failures.

**Why this matters:** This filter silently drops valid ad records from the sync output. If a user
reports missing ads data, Smart+ ads without `modify_time` values are the likely cause. This is a known
trade-off to maintain incremental sync reliability.

---

## 8. Authentication via Header Injection (Not OAuth)

Unlike most ad platform connectors, source-tiktok-marketing uses `ApiKeyAuthenticator` that injects the
access token as an `Access-Token` header, not a Bearer token or OAuth flow. The token is extracted from
either `config.credentials.access_token` or `config.access_token` (for backward compatibility).

TikTok's Marketing API does not use standard OAuth 2.0 refresh token flows. Access tokens are
long-lived and obtained through TikTok's developer portal or app authorization flow outside of Airbyte.

**Why this matters:** There is no token refresh mechanism in this connector. If a user's access token
expires or is revoked, the sync will fail with an authentication error and the user must manually
obtain and configure a new token. Do not attempt to add an `OAuthAuthenticator` without understanding
TikTok's specific auth requirements.
