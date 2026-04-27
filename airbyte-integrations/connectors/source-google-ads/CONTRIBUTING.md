# Contributing to source-google-ads

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Google Ads API uses GAQL (Google Ads Query Language) for data access. Report/metrics streams support date-based segmentation via `segments.date`, while resource configuration streams (ad groups, campaigns, etc.) do not support date-based WHERE clauses for modification tracking.

**Connector type:** Hybrid (manifest.yaml + Python custom components)

**Analysis status:** Complete stream-by-stream analysis performed. All report/metrics streams already use `DatetimeBasedCursor` on `segments.date`. Resource configuration streams are correctly full-refresh because GAQL does not support filtering by modification date. The `change_status` stream provides change tracking as a separate incremental stream.

### Already Incremental Streams

| Stream | Cursor Field | Mechanism | Notes |
|--------|-------------|-----------|-------|
| account_performance_report | segments.date | DatetimeBasedCursor | `incremental_stream_base` |
| click_view | segments.date | DatetimeBasedCursor | Custom requester + dedicated incremental_sync |
| geographic_view | segments.date | DatetimeBasedCursor | Report stream |
| geographic_view_with_metrics | segments.date | DatetimeBasedCursor | Report stream |
| shopping_performance_view | segments.date | DatetimeBasedCursor | Report stream |
| display_keyword_view | segments.date | DatetimeBasedCursor | Report stream |
| keyword_view | segments.date | DatetimeBasedCursor | Report stream |
| topic_view | segments.date | DatetimeBasedCursor | Report stream |
| user_location_view | segments.date | DatetimeBasedCursor | Report stream |
| change_status | change_status.last_change_date_time | DatetimeBasedCursor | Change tracking for resource mutations |
| ad_group_criterion (incremental) | segments.date | DatetimeBasedCursor | Criterion stream via `criterion_incremental_stream_base` |
| ad_listing_group_criterion (incremental) | segments.date | DatetimeBasedCursor | Criterion stream |
| campaign_criterion | segments.date | DatetimeBasedCursor | Criterion stream |
| Custom GAQL queries | segments.date | DatetimeBasedCursor | User-defined queries via `custom_queries_stream` |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| accessible_accounts | Account discovery; no timestamp | Returns list of accessible customer accounts; no date fields |
| customer_client | Account hierarchy; no timestamp | Returns customer-client relationships; no modification date in GAQL |
| customer_client_non_manager | Account hierarchy; no timestamp | Filtered variant of customer_client |
| ad_group | Resource config; no GAQL date filter | GAQL `ad_group` resource has no `last_modified` field; use `change_status` for change tracking |
| ad_group_ad | Resource config; no GAQL date filter | Same as ad_group |
| ad_group_ad_label | Resource config; no GAQL date filter | Join table; no modification timestamps |
| ad_group_ad_legacy | Resource config; no GAQL date filter | Legacy format of ad_group_ad |
| ad_group_bidding_strategy | Resource config; no GAQL date filter | Configuration object |
| ad_group_label | Resource config; no GAQL date filter | Join table |
| ad_group_criterion_label | Resource config; no GAQL date filter | Join table |
| audience | Resource config; no GAQL date filter | Audience definition objects |
| campaign | Resource config; no GAQL date filter | Campaign configuration; use `change_status` for change tracking |
| campaign_bidding_strategy | Resource config; no GAQL date filter | Configuration object |
| campaign_budget | Resource config; no GAQL date filter | Budget configuration |
| campaign_label | Resource config; no GAQL date filter | Join table |
| customer | Resource config; no GAQL date filter | Customer/account metadata |
| customer_label | Resource config; no GAQL date filter | Join table |
| label | Resource config; no GAQL date filter | Label definitions |
| user_interest | Reference data; no GAQL date filter | Google-defined taxonomy; does not change |
| ad_group_criterion (full refresh) | Resource config variant | Full-refresh variant via `criterion_full_refresh_stream_base` |
| ad_listing_group_criterion (full refresh) | Resource config variant | Full-refresh variant |
