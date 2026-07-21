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
`["end_date", "string_of_pivot_values"]`. Impression-device analytics also includes
`sponsoredCampaign` in its merge key so records for different campaigns are not combined.

**Why this matters:** With ~90 analytics fields defined, each analytics record requires approximately 5
separate HTTP requests to assemble. Campaign and impression-device analytics batch up to 50 campaign
URNs per partition, while creative analytics batches up to 50 creative URNs. Member-demographic
analytics remain on the `q=analytics` finder with one campaign per request because the `q=statistics`
finder does not support `MEMBER_*` pivots. Adding new analytics fields increases the chunk count and
silently multiplies API usage across every partition.

---

## 3. Analytics Request Batching (`batch_size`)

The analytics streams `ad_campaign_analytics`, `ad_creative_analytics`, and
`ad_impression_device_analytics` batch multiple parent-entity URNs into a single `adAnalytics` request
via `LinkedInAdsBatchedPartitionRouter` with `batch_size: 50`. Campaign and impression-device
analytics batch campaign URNs; creative analytics batches creative URNs. Compared with one request per
parent entity, a full 50-entity batch reduces analytics request volume by 98%.

Why 50 entities per request:

- LinkedIn does not document a maximum number of campaign URNs per request. The binding constraint is URL
  length: the query string is capped at 4 KB, and the raw URL is capped at 8 KB. Exceeding either limit
  returns HTTP 414 `REQUEST_URI_TOO_LONG`.
- Each URL-encoded campaign URN (`urn%3Ali%3AsponsoredCampaign%3A<id>`) is approximately 42 bytes: a 31-byte
  fixed prefix, an approximately 9–10 digit ID, and a comma separator. Each request also carries one field
  chunk, so the worst-case query length is approximately `643 + n × (32 + id_digits)` bytes.
- At `batch_size: 50`, the worst-case query string is approximately 3 KB, leaving approximately 900 bytes
  of headroom under the 4 KB cap even with long campaign IDs. A batch size of 60 is also safe, but 80
  exceeds the cap with IDs of 12 or more digits and is unsafe as a default.
- The connector fails fast on HTTP 414 with `LinkedIn Ads request URL exceeds the API length limit` rather
  than silently truncating the request.

The `adAnalytics` API does not support pagination and caps each response at 15,000 elements. Campaign
and creative analytics can return at most 1,550 daily rows per 50-entity `P30D` request.
Impression-device analytics can return at most 7,750 rows for the five documented device categories
over the same range. The record extractor fails if an analytics response reaches 15,000 elements
rather than emitting a potentially truncated response.

Batch membership can change when campaigns or creatives are added or removed, so the three batched
streams use a global substream cursor. Existing per-partition state is migrated once to the earliest
partition cursor, after which subsequent syncs emit global state and do not repeat the migration. The
one-time migration can re-read already-synced dates, but it does not skip an entity that was behind the
other partitions.

The emitted primary key for `ad_impression_device_analytics` remains
`["string_of_pivot_values", "end_date"]` for compatibility. Because `string_of_pivot_values` contains
only the device type, this pre-existing key does not distinguish campaigns. Correcting it requires a
major-version breaking change even though property-chunk merging already keeps campaigns separate.

The eight `ad_member_*` demographic streams are not batched. Batching requires a second `CAMPAIGN` pivot
to attribute each row back to its campaign, which only the multi-pivot `q=statistics` finder supports.
However, `q=statistics` does not accept `MEMBER_*` pivots. The `q=analytics` finder is single-pivot, so
member-demographic streams cannot batch campaigns and remain one request per campaign.

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

## 7. Unpublished Rate Limits with Per-Endpoint Daily Caps

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

LinkedIn separately limits Ad Analytics requests to 45 million metric values across a rolling five-minute
window. Metric values are calculated from the requested fields and returned records, so the call-count
budget cannot predict this limit. `LinkedInAdsDataVolumeBackoffStrategy` detects the documented response
message and waits 330 seconds before retrying. Analytics requests keep the existing five-retry limit but
allow up to 30 minutes so each retry starts after the rolling window can clear.

**Why this matters:** Do not replace the data-volume backoff with a faster generic 429 strategy. Count-based
429 responses must continue using the exponential fallback, and unrecognized response bodies must not be
treated as data-volume throttles.

## Incremental Stream Considerations

The LinkedIn Marketing API supports date-based filtering on analytics and campaign/creative endpoints, which the connector already uses for 17 incremental streams. The single remaining FR parent stream (`accounts`) is a config-style endpoint listing ad accounts, which does not support date-based filtering on its list endpoint.

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
| lead_form_responses | medium | child | none | none | deferred_child |  |
| lead_forms | medium | child | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (1 streams):** `accounts` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (2 streams):** `lead_form_responses`, `lead_forms` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
