import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# TikTok Marketing Migration Guide

## Upgrading to 5.0.0

The `currency` field in the `pixels` stream's `events` array has been corrected from `boolean` to `string` type. The TikTok API returns currency as a string value (e.g. `"USD"`), so the previous `boolean` type was incorrect and caused transform errors during syncs.

Users syncing the `pixels` stream must refresh the source schema and clear data for that stream after upgrading.

## Upgrading to 4.0.0

This version migrates source TikTok Marketing from the Python CDK to the low-code framework. Due to differences between the Python and low-code CDKs, this migration is a breaking change.

### State format changes

The state format has changed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition. The following streams are affected:

- `ad_group_audience_reports_by_country_daily`
- `ad_group_audience_reports_by_platform_daily`
- `ad_group_audience_reports_daily`
- `ad_groups`
- `ad_groups_reports_daily`
- `ad_groups_reports_hourly`
- `ads`
- `ads_audience_reports_by_country_daily`
- `ads_audience_reports_by_platform_daily`
- `ads_audience_reports_by_province_daily`
- `ads_audience_reports_daily`
- `ads_reports_daily`
- `ads_reports_hourly`
- `advertisers_audience_reports_by_country_daily`
- `advertisers_audience_reports_by_platform_daily`
- `advertisers_audience_reports_daily`
- `advertisers_reports_daily`
- `advertisers_reports_hourly`
- `campaigns`
- `campaigns_audience_reports_by_country_daily`
- `campaigns_audience_reports_by_platform_daily`
- `campaigns_audience_reports_daily`
- `campaigns_reports_daily`
- `campaigns_reports_hourly`
- `creative_assets_images`
- `creative_assets_videos`

After upgrading, clear data for each affected stream that your connection uses.

### Schema changes

The `advertiser_id` field in the `advertiser_ids` stream changed from `integer` to `string` to match the type declared in the TikTok API. After upgrading, refresh the source schema and clear data for the `advertiser_ids` stream.

## Connector upgrade guide

<MigrationGuide />
