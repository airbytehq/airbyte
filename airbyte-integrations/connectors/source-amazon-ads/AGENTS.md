> NOTE: CLAUDE.md is a symlink to AGENTS.md; update AGENTS.md (not the symlink) when changing these instructions.

# source-amazon-ads: Unique Behaviors

## 1. Async Report Generation with Polling and Download

Report streams use the `AsyncRetriever` pattern instead of standard REST pagination. The connector creates a report via POST, polls a separate endpoint for the report's completion status, and then downloads the finished report from a URL provided in the polling response. This three-phase workflow (create → poll → download) means report streams have fundamentally different timing characteristics than standard entity streams: each report slice involves multiple sequential HTTP requests with wait intervals between polls.

The connector enforces a configurable `max_concurrent_async_job_count` (default 10) to limit how many reports are being generated simultaneously across all streams.

**Why this matters:** Report streams cannot be treated like standard paginated streams. They require polling intervals, have separate error handlers for creation vs. polling phases, and can take minutes to complete per slice. If you add a new report stream, you must configure all three phases (creation requester, polling requester, download requester) and their respective error handlers independently.

## 2. HTTP 425 (Too Early) for Duplicate Report Requests

When a user syncs the same report type with different time granularities simultaneously (e.g., daily and monthly versions of the same report), Amazon detects these as duplicate requests and returns HTTP 425. The connector treats this as a config error because the only fix is to either use separate sources for different granularities or set the number of concurrent threads to 2 for sequential processing.

**Why this matters:** HTTP 425 is extremely rare in REST APIs and is not handled by default error handlers. If you see a config error mentioning "duplicate report requests," it is not a credential or permission issue — it is a concurrency conflict that requires changing the source configuration or splitting into separate connections.

## 3. Report Columns Are Opt-In, and Missing Ones Fail Silently

Amazon's v3 reporting API returns only the columns named in `configuration.columns`. Omitting a column is not an error — the report simply comes back without it, so a stream can look healthy while silently withholding most of what the report type offers. This is how `sponsored_brands_campaigns_report_stream` shipped requesting 18 of the 65 documented `sbCampaigns` columns, which produced [oncall#13131](https://github.com/airbytehq/oncall/issues/13131).

The gap opens when a stream is scoped to a reporting *need* instead of to its report *type*. Both Sponsored Brands report streams arrived in [#78487](https://github.com/airbytehq/airbyte/pull/78487) as "Sponsored Brands cost reports", and their column lists were exactly that task's cost and conversion metrics: budget and identity fields, `clicks`, `cost`, `impressions`, `sales`, `purchases`, `unitsSold`, and the six new-to-brand metrics. Everything else `sbCampaigns` offers — including every video metric — was never requested. Nothing forced the omission into view, because Amazon returns 200 either way and no test compared the requested columns against the report type's documented set.

The authoritative column list per report type is at `https://d3a0d0y2hgofx6.cloudfront.net/en-us/guides/reporting/v3/report-types/<page>.md` (the rendered docs site is a JS shell that does not crawl; the CloudFront `.md` files are the same content as raw markdown). Column types live in `guides/reporting/v3/columns.md`. The available set for a stream is the report type's base metrics plus the "Additional metrics" of every value in its `groupBy`.

**Why this matters:** when you add or touch a report stream, request the report type's full documented column set and declare every requested column in the inline schema. `test_requested_report_columns_and_schema_properties_match_exactly` ties the two together in both directions, so it catches an undeclared column and an orphaned property left behind by a removal — but it is structural and knows nothing about which columns Amazon will actually accept. Validate a new column list against the live API (regression tests or a pre-release pin) before merging.

## 4. `timeUnit` Determines Which Date Columns Are Legal

`DAILY` reports carry the `date` column; `SUMMARY` reports carry `startDate`/`endDate`. The pairing is not interchangeable — requesting `date` on a `SUMMARY` report fails. `test_report_date_columns_match_time_unit` guards this. Note that `reportDate` is not an Amazon column at all: `transformation_report_add_fields` synthesises it from `stream_interval.end_time` on every report stream, daily ones included.

## 5. Sponsored Brands Creative Type Lives on the Ad Entity, Not on Reports

No v3 Sponsored Brands *report* exposes creative type or ad format — `adFormat` belongs to the `benchmarks` report and `creativeType` to Amazon DSP. Sponsored Brands V4 moved creative type onto the ad entity, so the only way to tell a video ad from a collection ad is `sponsored_brands_ads` (`POST sb/v4/ads/list`) → `creative.type`, joined to report rows on `adId`. The V2 streams that used a `creativeType=video` report filter were removed in 6.0.0 and have no direct equivalent.

**Why this matters:** requests to "split Sponsored Brands reporting by video" cannot be answered by adding a report column. They need the ad entity stream plus a join. The video *metrics* themselves (`video5SecondViews`, `videoCompleteViews`, and so on) are ordinary report columns and differ per report type — the connector requests `viewClickThroughRate` on `sbCampaigns` only, and omits `viewableImpressions` on `sbAdGroup`. Amazon's two references disagree here: the ad group and ad report-type pages omit both metrics where the connector omits them, while `columns.md` lists `sbAdGroups` and `sbAds` under the "Report types" of both. The connector follows the report-type pages because a single unaccepted column fails the whole report request and returns no rows; do not widen these sets without a live run.

## Incremental Stream Considerations

The Amazon Ads API uses report-based data access for most metrics. The `profiles` endpoint lists advertising profiles and does not support date-based filtering — it returns the current list of profiles. The connector already uses `DatetimeBasedCursor` for report streams (sponsored products, brands, display). The two FR parent streams (`profiles`, `profiles_filtered`) are small config-style lookups.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| profiles | small | top-level parent | none | none | deferred_no_api_support | Config-style; lists advertising profiles, no date filter |
| profiles_filtered | small | top-level parent | none | none | deferred_no_api_support | Filtered variant of profiles endpoint |
| sponsored_brands_ads_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_brands_ads_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
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
| sponsored_products_search_terms_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_search_terms_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| sponsored_products_targets_report_stream | medium | top-level parent | reportDate | reportDate | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor` |
| sponsored_products_targets_report_stream_daily | medium | top-level parent | date | date | incremental | `DatetimeBasedCursor` via `incremental_sync_report_datetime_cursor_daily` |
| attribution_report_performance_adgroup | medium | child of profiles_filtered | none | none | deferred_child |  |
| attribution_report_performance_campaign | medium | child of profiles_filtered | none | none | deferred_child |  |
| attribution_report_performance_creative | medium | child of profiles_filtered | none | none | deferred_child |  |
| attribution_report_products | medium | child of profiles_filtered | none | none | deferred_child |  |
| portfolios | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_brands_ad_groups | medium | child of profiles_filtered | none | none | deferred_child |  |
| sponsored_brands_ads | medium | child of profiles_filtered | none | none | deferred_child |  |
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
- **Child streams (24 streams):** `attribution_report_performance_adgroup`, `attribution_report_performance_campaign`, `attribution_report_performance_creative`, `attribution_report_products`, `portfolios`, `sponsored_brands_ad_groups`, `sponsored_brands_ads`, `sponsored_brands_campaigns`, `sponsored_brands_keywords`, `sponsored_display_ad_groups`, `sponsored_display_budget_rules`, `sponsored_display_campaigns`, `sponsored_display_creatives`, `sponsored_display_product_ads`, `sponsored_display_targetings`, `sponsored_product_ad_group_bid_recommendations`, `sponsored_product_ad_group_suggested_keywords`, `sponsored_product_ad_groups`, `sponsored_product_ads`, `sponsored_product_campaign_negative_keywords`, `sponsored_product_campaigns`, `sponsored_product_keywords`, `sponsored_product_negative_keywords`, `sponsored_product_targetings` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
