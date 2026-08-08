# Contributing to source-tiktok-marketing

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for advertiser ID partitioning and metrics transformation)

**Analysis status:** Complete. 44 streams analyzed (28 unconditional + 16 production-only via ConditionalStreams). 30 use incremental sync with date-based cursors. 14 are full-refresh.

### Incremental Streams (30)

| Category | Streams | Cursor | Notes |
|----------|---------|--------|-------|
| Management | ads, ad_groups, campaigns | `modify_time` | TikTok Ads Management API with date filter |
| Creative assets | creative_assets_images, creative_assets_videos | `modify_time` | TikTok Creative API |
| Daily reports (19) | ads/ad_groups/campaigns daily + audience reports, advertisers daily + audience reports, ads/ad_groups reports by country daily, ads audience by province daily | `stat_time_day` | TikTok Reporting API |
| Hourly reports (6) | ads/ad_groups/campaigns hourly, advertisers hourly, ads/ad_groups reports by country hourly | `stat_time_hour` | TikTok Reporting API |

Note: 12 of the 30 incremental streams are production-only (gated by ConditionalStreams; excluded in sandbox mode).

### Full-Refresh Streams (14)

| Stream | Reason | Evidence |
|--------|--------|----------|
| advertisers | Top-level enumeration; no date filter | TikTok Advertisers API returns all accounts |
| advertiser_ids | Production-only enumeration; no date filter | Returns advertiser IDs for multi-advertiser accounts |
| audiences | No date filter | TikTok Audience Management API has no `updated_since` |
| ad_groups_reports_lifetime | Lifetime aggregation; no date cursor | Single lifetime aggregate per ad group |
| ads_reports_lifetime | Lifetime aggregation; no date cursor | Single lifetime aggregate per ad |
| campaigns_reports_lifetime | Lifetime aggregation; no date cursor | Single lifetime aggregate per campaign |
| advertisers_reports_lifetime | Lifetime aggregation; no date cursor | Production-only; single lifetime aggregate per advertiser |
| advertisers_audience_reports_lifetime | Lifetime aggregation; no date cursor | Production-only; audience breakdown per advertiser |
| creative_assets_music | No date filter | TikTok Music Library API has no `modify_time` filter |
| creative_assets_portfolios | No date filter | TikTok Portfolio API has no `modify_time` filter |
| spark_ads | Production-only; no date filter | TikTok Spark Ads API has no `modify_time` filter |
| pixels | Production-only; no date filter | TikTok Pixel management endpoint |
| pixel_instant_page_events | Production-only; no date filter | TikTok Pixel events endpoint |
| pixel_events_statistics | Production-only; no date filter | TikTok Pixel statistics endpoint |
