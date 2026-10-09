# source-amazon-ads: Unique Behaviors

## 1. Async Report Generation with Polling and Download

Report streams use the `AsyncRetriever` pattern instead of standard REST pagination. The connector creates a report via POST, polls a separate endpoint for the report's completion status, and then downloads the finished report from a URL provided in the polling response. This three-phase workflow (create → poll → download) means report streams have fundamentally different timing characteristics than standard entity streams: each report slice involves multiple sequential HTTP requests with wait intervals between polls.

The connector enforces a configurable `max_concurrent_async_job_count` (default 10) to limit how many reports are being generated simultaneously across all streams.

**Why this matters:** Report streams cannot be treated like standard paginated streams. They require polling intervals, have separate error handlers for creation vs. polling phases, and can take minutes to complete per slice. If you add a new report stream, you must configure all three phases (creation requester, polling requester, download requester) and their respective error handlers independently.

## 2. HTTP 425 (Too Early) for Duplicate Report Requests

Amazon returns HTTP 425 when it considers a report request a duplicate of one it is still generating, usually with a body naming that report: `The Request is a duplicate of : <reportId>`. The usual trigger is a retried sync attempt. Report request bodies are deterministic for a given slice, so when an earlier attempt requested a report and died before collecting it, the retry sends the same request. `DuplicateReportCreationRequester` (the shared `creation_requester` for all report streams) looks up the named report with the polling request and reuses it only if it has not FAILED and matches this request's dates, report type, time unit, columns, grouping, and filters. A reused report gets a stand-in creation response carrying its ID, so the polling requester picks it up and the download flow runs unchanged. A 425 that names no report, or names one that does not match or cannot be read (403 or 404 on the lookup), is requested again after a 60-second wait, up to four requests in all. If it persists, the request fails as a transient error, because the duplicate clears once the earlier report finishes.

The wrapper sends the POST through `creation_requester.requester`, an ordinary `HttpRequester`, and the lookup through `creation_requester.report_requester`, which reuses the polling requester with `report_lookup_error_handler`. Report streams therefore override `creation_requester.requester.request_body_json`. A `request_body_json` placed directly on `creation_requester` is silently ignored, and `test_report_stream_discovery_covers_every_report_stream` fails if a report stream's body is not where the guard tests look for it. Keep the nesting: a subclass of `HttpRequester` built as a custom component loses the CDK's wiring (request options other than headers and JSON body, test-read logging, disabled retries in test reads).

**Why this matters:** HTTP 425 is extremely rare in REST APIs and is not handled by default error handlers. `report_creation_error_handler` maps it to IGNORE so the response reaches the requester. Do not map it to FAIL with `config_error`: a config error stops every report job in the stream and the platform does not retry it, so one leftover report from a failed attempt fails the whole job ([oncall#13620](https://github.com/airbytehq/oncall/issues/13620)). An earlier version of this section blamed syncing summary and daily variants of a report together. Those requests differ in `timeUnit`, columns, and name, so Amazon does not treat them as identical, and the oncall#13620 failures were on connections that sync a single stream.

## 3. Report Columns Are Opt-In

Amazon's v3 reporting API returns only the columns listed in a report stream's `configuration.columns`. Leaving one out is not an error, so an under-specified stream syncs cleanly while withholding data. Streams here request the full documented column set for their report type, minus the handful Amazon rejects for that stream's `groupBy`; keep it that way when adding or editing one, and declare every requested column in the inline schema so users can see the record shape before syncing.

Under-specified streams come from scoping a stream to a reporting need rather than to its report type. The Sponsored Brands campaign and ad group reports were added in [#78487](https://github.com/airbytehq/airbyte/pull/78487) for cost reporting and requested only that task's cost and conversion metrics, which is how every Sponsored Brands video metric went missing.

Two rules to know. `DAILY` reports use the `date` column while `SUMMARY` reports use `startDate`/`endDate`. And Amazon rejects a column that is not valid for the stream's `groupBy` with a 400 or 422, failing the whole report rather than dropping the column, so the stream returns nothing at all — validate new column lists against the live API before merging.

## 4. Sponsored Brands Creative Type Is Not a Report Column

No v3 Sponsored Brands report exposes creative type or ad format. Sponsored Brands V4 moved creative type onto the ad entity, so identifying video ads means syncing `sponsored_brands_ads` and joining `creative.type` to report rows on `adId`. The video *metrics* are ordinary report columns, but the connector does not request them uniformly: `viewClickThroughRate` is requested on `sbCampaigns` only, and `viewableImpressions` is omitted on `sbAdGroup`. Amazon's report-type pages and its column reference disagree on those cells; the connector follows the report-type pages, because one unaccepted column fails the entire report request and returns no rows.

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
