# Contributing to source-snapchat-marketing

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The Snapchat Marketing API supports date-based filtering on stats endpoints and `updated_at` ordering on entity endpoints, which the connector already uses for 16 incremental streams. The 4 remaining streams are children partitioned via `SubstreamPartitionRouter` (ad_squad_stats, ad_stats, campaign_stats, organization_stats). No FR parent streams remain.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| organizations | medium | top-level parent | updated_at | updated_at | incremental |  |
| adaccounts | medium | child | updated_at | updated_at | incremental |  |
| adaccounts_stats_daily | medium | child | start_time | start_time | incremental |  |
| adaccounts_stats_hourly | medium | child | start_time | start_time | incremental |  |
| adaccounts_stats_lifetime | medium | child | none | none | deferred_child |  |
| ads | medium | child | updated_at | updated_at | incremental |  |
| ads_stats_daily | medium | child | start_time | start_time | incremental |  |
| ads_stats_hourly | medium | child | start_time | start_time | incremental |  |
| ads_stats_lifetime | medium | child | none | none | deferred_child |  |
| adsquads | medium | child | updated_at | updated_at | incremental |  |
| adsquads_stats_daily | medium | child | start_time | start_time | incremental |  |
| adsquads_stats_hourly | medium | child | start_time | start_time | incremental |  |
| adsquads_stats_lifetime | medium | child | none | none | deferred_child |  |
| campaigns | medium | child | updated_at | updated_at | incremental |  |
| campaigns_stats_daily | medium | child | start_time | start_time | incremental |  |
| campaigns_stats_hourly | medium | child | start_time | start_time | incremental |  |
| campaigns_stats_lifetime | medium | child | none | none | deferred_child |  |
| creatives | medium | child | updated_at | updated_at | incremental |  |
| media | medium | child | updated_at | updated_at | incremental |  |
| segments | medium | child | updated_at | updated_at | incremental |  |

### Future incremental stream candidates

- **Child streams (4 streams):** `adaccounts_stats_lifetime`, `ads_stats_lifetime`, `adsquads_stats_lifetime`, `campaigns_stats_lifetime` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
