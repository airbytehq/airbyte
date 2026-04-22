# source-linkedin-ads: Unique Connector Behaviors

This document describes the biggest non-obvious gotchas in `source-linkedin-ads` that deviate from standard
declarative connector patterns. Read this before making changes to the connector.

---

## 1. Safe URL Encoding for LinkedIn's REST API Syntax

LinkedIn's REST API uses a proprietary query parameter syntax with special characters like parentheses,
colons, commas, and percent-encoded URNs (e.g., `pivot=(value:CAMPAIGN)`,
`campaigns=List(urn%3Ali%3AsponsoredCampaign%3A123)`). Standard HTTP clients encode these characters
during URL preparation, which breaks the API requests.

The connector uses a custom `SafeHttpClient` and `SafeEncodeHttpRequester` that override the prepared
request logic to call `urlencode(query_params, safe="():,%")`, preserving these characters verbatim in
the URL.

**Why this matters:** If you switch analytics streams to use the standard `HttpRequester`, every
analytics API call will fail because the parentheses and colons in pivot values and URN lists will get
double-encoded. This affects all analytics streams (ad_campaign_analytics, ad_creative_analytics, and
all ad_member_*_analytics streams).

---

## 2. Analytics Property Chunking with 18-Field Limit

LinkedIn's Ad Analytics API (`GET /adAnalytics`) requires you to specify which metric fields to return
via the `fields` query parameter. The API enforces a maximum of 20 fields per request. The connector
uses `QueryProperties` with `PropertyChunking` configured at a limit of 18 fields per chunk (reserving
2 slots for the mandatory `dateRange` and `pivotValues` fields that are always included).

Records from multiple chunks are stitched back together using `GroupByKeyMergeStrategy` keyed on
`["end_date", "string_of_pivot_values"]`.

**Why this matters:** With ~90 analytics fields defined, each analytics record requires approximately 5
separate HTTP requests to assemble. Every analytics stream is also partitioned by parent entity (one
campaign or creative per partition), so the total API call count is roughly
`num_entities * num_date_slices * 5`. Adding new analytics fields increases the chunk count and
silently multiplies API usage across every partition.

---

## 3. DNS Resolution Errors Treated as Transient

The `LinkedInAdsErrorHandler` catches Python `InvalidURL` exceptions and classifies them as transient
(retryable) errors rather than failing the sync. This is a workaround for intermittent DNS resolution
failures that surface as `InvalidURL` exceptions in the requests library.

**Why this matters:** Without this handler, a temporary DNS blip during a long-running sync would
permanently fail the entire sync instead of retrying. If you replace or modify the error handler, make
sure `InvalidURL` exceptions are still caught and retried, or syncs on unstable networks will fail
intermittently.

---

## 4. Millisecond Timestamps and Multiple Datetime Formats

LinkedIn's API returns timestamps in inconsistent formats across different endpoints. Entity streams
(accounts, campaigns, creatives) return `lastModified` and `created` as millisecond Unix timestamps
(e.g., `1629581275000`), while analytics streams use date objects with nested `year/month/day` fields.
The `LinkedInAdsRecordExtractor` converts millisecond timestamps to RFC3339 format during extraction.

The manifest declares multiple `cursor_datetime_formats` per stream: `"%ms"` for millisecond
timestamps, `"%Y-%m-%dT%H:%M:%S%z"` for ISO 8601, and `"%Y-%m-%d"` for date-only analytics cursors.

**Why this matters:** If you add a new incremental stream, you must check which timestamp format that
specific LinkedIn endpoint returns and configure the correct `cursor_datetime_formats` list. Using the
wrong format will cause cursor comparisons to silently fail, either re-syncing all data on every run
or skipping records entirely.

---

## 5. Reserved Keyword Renaming for Destination Compatibility

The `transform_data` function renames the `pivot` field to `_pivot` in every analytics record. This is
because `PIVOT` is a reserved keyword in Amazon Redshift, and using it as a column name causes
normalization failures at the destination.

**Why this matters:** If you add new fields to analytics streams, check whether the field name
conflicts with reserved keywords in common destinations (Redshift, BigQuery, Snowflake). The
`DESTINATION_RESERVED_KEYWORDS` list in `components.py` is the mechanism for handling these conflicts
-- add any new reserved words there rather than creating a separate transformation.

---

## 6. Unpublished Rate Limits with Per-Endpoint Daily Caps

LinkedIn does not publish standard API rate limits. The connector's comments document that each endpoint
has its own individually tracked rate limit that resets daily, with tiers that vary by account. The
connector's OAuth app supports 15,000,000 requests/day for `/adAnalytics` endpoints specifically.

The `api_budget` is configured conservatively at 6 requests per 10 seconds for analytics endpoints, and
the default concurrency is set to 6 workers (configurable via `num_workers` up to 50). This was reduced
from a higher default after customers experienced rate limiting issues.

**Why this matters:** Because rate limits are per-endpoint and unpublished, there is no reliable way to
predict when a customer will hit limits. If customers report rate limiting, the `num_workers` config
value is the primary lever to reduce pressure. The analytics property chunking (5 requests per record
page) means the effective request rate is much higher than the visible concurrency level suggests.
