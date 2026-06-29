# source-amazon-ads: Unique Behaviors

## 1. Async Report Generation with Polling and Download

Report streams use the `AsyncRetriever` pattern instead of standard REST pagination. The connector creates a report via POST, polls a separate endpoint for the report's completion status, and then downloads the finished report from a URL provided in the polling response. This three-phase workflow (create → poll → download) means report streams have fundamentally different timing characteristics than standard entity streams: each report slice involves multiple sequential HTTP requests with wait intervals between polls.

The connector enforces a configurable `max_concurrent_async_job_count` (default 10) to limit how many reports are being generated simultaneously across all streams.

**Why this matters:** Report streams cannot be treated like standard paginated streams. They require polling intervals, have separate error handlers for creation vs. polling phases, and can take minutes to complete per slice. If you add a new report stream, you must configure all three phases (creation requester, polling requester, download requester) and their respective error handlers independently.

## 2. HTTP 425 (Too Early) for Duplicate Report Requests

When a user syncs the same report type with different time granularities simultaneously (e.g., daily and monthly versions of the same report), Amazon detects these as duplicate requests and returns HTTP 425. The connector treats this as a config error because the only fix is to either use separate sources for different granularities or set the number of concurrent threads to 2 for sequential processing.

**Why this matters:** HTTP 425 is extremely rare in REST APIs and is not handled by default error handlers. If you see a config error mentioning "duplicate report requests," it is not a credential or permission issue — it is a concurrency conflict that requires changing the source configuration or splitting into separate connections.

## Incremental Stream Considerations

The Amazon Ads API uses report-based data access for most metrics. The `profiles` endpoint lists advertising profiles and does not support date-based filtering — it returns the current list of profiles. The connector already uses `DatetimeBasedCursor` for report streams (sponsored products, brands, display). The two FR parent streams (`profiles`, `profiles_filtered`) are small config-style lookups.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| profiles | small | top-level parent | none | none | deferred_no_api_support | Config-style; lists advertising profiles, no date filter |
| profiles_filtered | small | top-level parent | none | none | deferred_no_api_support | Filtered variant of profiles endpoint |
| sponsored_brands_v3_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_brands_v3_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_display_adgroups_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_display_adgroups_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_display_asins_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_display_asins_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_display_campaigns_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_display_campaigns_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_display_productads_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_display_productads_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_display_targets_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_display_targets_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_adgroups_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_adgroups_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_asins_keywords_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_asins_keywords_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_asins_targets_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_asins_targets_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_campaigns_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_campaigns_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_keywords_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_keywords_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_productads_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_productads_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_targets_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_targets_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| attribution_report_performance_adgroup | medium | child of profiles_filtered | none | none | deferred_child |  |
| attribution_report_performance_campaign | medium | child of profiles_filtered | none | none | deferred_child |  |
| attribution_report_performance_creative | medium | child of profiles_filtered | none | none | deferred_child |  |
| attribution_report_products | medium | child of profiles_filtered | none | none | deferred_child |  |
| portfolios | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_brands_ad_groups | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_brands_campaigns | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_brands_keywords | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_display_ad_groups | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_display_budget_rules | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_display_campaigns | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_display_creatives | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_display_product_ads | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_display_targetings | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_product_ad_group_bid_recommendations | medium | child of sponsored_product_ad_groups | none | none | deferred_child |  |
| sponsored_product_ad_group_suggested_keywords | medium | child of sponsored_product_ad_groups | none | none | deferred_child |  |
| sponsored_product_ad_groups | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_product_ads | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_product_campaign_negative_keywords | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_product_campaigns | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_product_keywords | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_product_negative_keywords | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_product_targetings | medium | child of profiles_filtered | none | none | deferred_child |  |

### Future incremental stream candidates

- **No API date filter (2 streams):** `profiles`, `profiles_filtered` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (23 streams):** `attribution_report_performance_adgroup`, `attribution_report_performance_campaign`, `attribution_report_performance_creative`, `attribution_report_products`, `portfolios`, `sponsored_brands_ad_groups`, `sponsored_brands_campaigns`, `sponsored_brands_keywords`, `sponsored_display_ad_groups`, `sponsored_display_budget_rules`, `sponsored_display_campaigns`, `sponsored_display_creatives`, `sponsored_display_product_ads`, `sponsored_display_targetings`, `sponsored_product_ad_group_bid_recommendations`, `sponsored_product_ad_group_suggested_keywords`, `sponsored_product_ad_groups`, `sponsored_product_ads`, `sponsored_product_campaign_negative_keywords`, `sponsored_product_campaigns`, `sponsored_product_keywords`, `sponsored_product_negative_keywords`, `sponsored_product_targetings` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
