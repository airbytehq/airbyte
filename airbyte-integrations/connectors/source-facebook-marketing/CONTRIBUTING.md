# Contributing to source-facebook-marketing

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Facebook Marketing API supports date-based filtering via `time_range` and `filtering` parameters on Ads, AdSets, and Campaigns. The connector is a Python CDK connector with `FBMarketingIncrementalStream` (server-side `updated_time` filtering) and `FBMarketingReversedIncrementalStream` (reversed pagination with client-side cursor) providing incremental patterns.

**Connector type:** Python CDK

**Analysis status:** Complete stream-by-stream analysis performed. All high-volume streams already use incremental sync. Remaining full-refresh streams either lack API-level date filtering or are single-record endpoints.

### Already Incremental Streams

| Stream | Sync Mode | Cursor Field | Base Class | Notes |
|--------|-----------|-------------|------------|-------|
| Ads | incremental | updated_time | FBMarketingIncrementalStream | Server-side filtering via `filtering` param |
| AdSets | incremental | updated_time | FBMarketingIncrementalStream | Server-side filtering via `filtering` param |
| Campaigns | incremental | updated_time | FBMarketingIncrementalStream | Server-side filtering via `filtering` param |
| Activities | incremental | event_time | FBMarketingIncrementalStream | Server-side filtering |
| Videos | incremental | updated_time | FBMarketingReversedIncrementalStream | Reversed pagination with client-side cursor |
| Images | incremental | updated_time | FBMarketingReversedIncrementalStream | Reversed pagination with client-side cursor |
| AdsInsights (+ all breakdowns) | incremental | date_start | AdsInsights | Date-range windowed requests; 16+ breakdown variants |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| AdCreatives | No date-based filtering | Facebook Graph API `/adcreatives` endpoint does not support `filtering` by `updated_time`; objects lack a reliable modification timestamp for cursor tracking |
| AdCreativesFromAds | Derived from Ads edge | Fetches creative data via each Ad's `adcreatives` edge; same limitation as AdCreatives |
| CustomConversions | No date-based filtering; small dataset | `/customconversions` endpoint has no date filter; typically fewer than 100 rules per account |
| CustomAudiences | No server-side date filtering | Has `time_updated` field on records but Facebook Graph API `/customaudiences` endpoint does not accept date-based filtering params; client-side semi-incremental possible but low value given typical dataset size |
| AdAccount | Single record per account | Returns one record per ad account; no incremental benefit |
