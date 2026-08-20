> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

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
separate HTTP requests to assemble. For the three batched streams, the total API call count is roughly
`ceil(num_entities / 50) * num_date_slices * 5`; unbatched member-demographic and custom report streams
still issue requests per campaign. Adding analytics fields increases the chunk count and silently
multiplies API usage across every partition.

---

## 3. Analytics Request Batching and Stream Constraints

Only these analytics streams batch parent entities with the CDK `GroupingPartitionRouter` at
`group_size: 50`:

- `ad_campaign_analytics` batches campaign URNs with the single `CAMPAIGN` pivot.
- `ad_creative_analytics` batches creative URNs with the single `CREATIVE` pivot.
- `ad_impression_device_analytics` batches campaign URNs with
  `q=statistics&pivots=List(CAMPAIGN,IMPRESSION_DEVICE_TYPE)`.

A full group reduces entity-partition requests from 50 to 1. The group size leaves headroom under
LinkedIn's approximately 4 KB query-string limit; larger defaults can exceed the limit when URNs contain
long IDs.

The three streams use `global_substream_cursor: true` because grouping changes partition membership. Do
not add a custom minimum-cursor state migration: regression testing showed that rows present only in the
legacy control reads were previously synced records at or before stale per-entity cursors. Replaying from
the minimum cursor would create unnecessary duplicate reads.

The eight `ad_member_*` demographic streams must remain unbatched on the single-pivot `q=analytics`
finder. Batching would require adding a `CAMPAIGN` pivot for attribution, but LinkedIn's multi-pivot
`q=statistics` finder rejects all `MEMBER_*` pivots with `FIELD_INVALID`.

Impression-device records require special pivot handling. The extractor removes the leading campaign URN
from `pivotValues`, writes it to `sponsoredCampaign`, and leaves the device value as the stream pivot. Its
primary key is `["string_of_pivot_values", "end_date", "sponsoredCampaign"]`; omitting the campaign field
causes deduplicating destinations to collapse rows from different campaigns that share a device type and
date.

**Why this matters:** Do not generalize batching to unsupported member pivots, remove the global cursors,
reintroduce a minimum-cursor migration, or remove `sponsoredCampaign` from the impression-device primary
key.

---

## 4. DNS Resolution Errors Treated as Transient

The `LinkedInAdsErrorHandler` catches Python `InvalidURL` exceptions and classifies them as transient
(retryable) errors rather than failing the sync. This is a workaround for intermittent DNS resolution
failures that surface as `InvalidURL` exceptions in the requests library.

**Why this matters:** Without this handler, a temporary DNS blip during a long-running sync would
permanently fail the entire sync instead of retrying. If you replace or modify the error handler, make
sure `InvalidURL` exceptions are still caught and retried, or syncs on unstable networks will fail
intermittently.

---

## 5. Millisecond Timestamps and Multiple Datetime Formats

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

## 6. Reserved Keyword Renaming for Destination Compatibility

The `transform_data` function renames the `pivot` field to `_pivot` in every analytics record. This is
because `PIVOT` is a reserved keyword in Amazon Redshift, and using it as a column name causes
normalization failures at the destination.

**Why this matters:** If you add new fields to analytics streams, check whether the field name
conflicts with reserved keywords in common destinations (Redshift, BigQuery, Snowflake). The
`DESTINATION_RESERVED_KEYWORDS` list in `components.py` is the mechanism for handling these conflicts
-- add any new reserved words there rather than creating a separate transformation.

---

## 7. Analytics Rate Limits and Backoff

LinkedIn does not publish standard API rate limits. The connector's comments document that each endpoint
has its own individually tracked rate limit that resets daily, with tiers that vary by account. The
connector's OAuth app supports 15,000,000 requests/day for `/adAnalytics` endpoints specifically.

The `api_budget` is configured conservatively at 6 requests per 10 seconds for analytics endpoints, and
the default concurrency is set to 6 workers (configurable via `num_workers` up to 50). This was reduced
from a higher default after customers experienced rate limiting issues.

LinkedIn separately documents a limit of 45 million Ad Analytics metric values across a rolling
five-minute window. `LinkedInAdsDataVolumeBackoffStrategy` identifies only the HTTP 429 response whose
body mentions both the data-request limit and 45 million metric values, then waits 330 seconds before
retrying. Analytics requesters allow five retries and up to 30 minutes so each retry can begin after the
rolling window clears. Other retryable responses, including unrecognized 429 bodies, use exponential
fallback.

**Why this matters:** Because most endpoint limits are unpublished, there is no reliable way to predict
when a customer will hit them. If customers report count-based throttling, `num_workers` is the primary
lever to reduce pressure. Batching reduces request count and latency, but it does not reduce equivalent
metric-value workload or avoid the 45-million-value limit. Do not apply the 330-second delay to every 429
or replace the body-aware strategy with a faster generic backoff.

## Incremental Stream Considerations

The LinkedIn Marketing API supports date-based filtering on analytics and campaign/creative endpoints, which the connector already uses for 18 incremental streams. The single remaining FR parent stream (`accounts`) is a config-style endpoint listing ad accounts, which does not support date-based filtering on its list endpoint.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| accounts | small | top-level parent | none | none | deferred_no_api_support | Lists ad accounts; config-style, typically <10 accounts per org |
| account_users | medium | child | lastModified | lastModified | incremental |  |
| ad_campaign_analytics | medium | child | end_date | end_date | incremental |  |
| ad_creative_analytics | medium | child | end_date | end_date | incremental |  |
| ad_impression_device_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_company_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_company_size_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_country_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_industry_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_job_function_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_job_title_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_region_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_seniority_analytics | medium | child | end_date | end_date | incremental |  |
| campaign_groups | medium | child | lastModified | lastModified | incremental |  |
| campaigns | medium | child | lastModified | lastModified | incremental |  |
| conversions | medium | child | lastModified | lastModified | incremental |  |
| creatives | medium | child | lastModifiedAt | lastModifiedAt | incremental |  |
| custom_analytics_report | medium | child | end_date | end_date | incremental |  |
| custom_statistics_report | medium | child | end_date | end_date | incremental |  |
| lead_form_responses | medium | child | none | none | deferred_child |  |
| lead_forms | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (1 streams):** `accounts` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (2 streams):** `lead_form_responses`, `lead_forms` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
