# Contributing to source-tiktok-marketing

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for advertiser ID partitioning and metrics transformation)

**Analysis status:** Complete. 29 streams analyzed. 21 use incremental sync with date-based cursors. 8 are full-refresh.

### Incremental Streams (21)

| Category | Streams | Cursor | Notes |
|----------|---------|--------|-------|
| Management | ads, ad_groups, campaigns | `modify_time` | TikTok Ads Management API with date filter |
| Creative assets | creative_assets_images, creative_assets_videos | `modify_time` | TikTok Creative API |
| Daily reports (9) | ads/ad_groups/campaigns daily + audience reports | `stat_time_day` | TikTok Reporting API |
| Hourly reports (3) | ads/ad_groups/campaigns hourly | `stat_time_hour` | TikTok Reporting API |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| advertisers | Top-level enumeration; no date filter | TikTok Advertisers API returns all accounts |
| audiences | No date filter | TikTok Audience Management API has no `updated_since` |
| ad_groups_reports_lifetime | Lifetime aggregation; no date cursor | Single lifetime aggregate per ad group |
| ads_reports_lifetime | Lifetime aggregation; no date cursor | Single lifetime aggregate per ad |
| campaigns_reports_lifetime | Lifetime aggregation; no date cursor | Single lifetime aggregate per campaign |
| creative_assets_music | No date filter | TikTok Music Library API has no `modify_time` filter |
| creative_assets_portfolios | No date filter | TikTok Portfolio API has no `modify_time` filter |
