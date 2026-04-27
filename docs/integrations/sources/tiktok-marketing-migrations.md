import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# TikTok Marketing Migration Guide

## Upgrading to 5.0.0

The `currency` field in the `pixels` stream's `events` array has been corrected from `boolean` to `string` type. The TikTok API returns currency as a string value (e.g. `"USD"`), so the previous `boolean` type was incorrect and caused transform errors during syncs.

Users syncing the `pixels` stream need to refresh the source schema and clear data for that stream after upgrading.

### Migration steps

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK** and **Save changes**.
3. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `pixels` stream and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

## Upgrading to 4.0.0

This version migrated source TikTok Marketing from the Python CDK to the declarative low-code CDK. Due to changes in how state is managed for incremental streams nested within a parent stream, this migration constitutes a breaking change.

The following streams are affected:

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

See [Clearing data](#clearing-data) to update your connection.

The `advertiser_ids` stream schema also changed: the `advertiser_id` field type was corrected from integer to string to match the API response. Users need to refresh the stream schema.

See [Refresh schemas](#refresh-schemas) to update your connection.

### Migration steps

#### Refresh schemas

Refresh the `advertiser_ids` schema to continue syncing that stream:

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK** and **Save changes**.
3. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
4. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the `advertiser_ids` stream and select **Clear Data**.

Important: If you were using `advertiser_ids` without provided advertiser_id in the source configuration you should firstly refresh source schema for `advertiser_ids` stream and then clear data for affected streams from the list above.

#### Clearing data

Clear data for the affected streams listed above:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the impacted stream and select **Clear Data**.
3. Do the same steps from 1-2.1 for all streams in your connection that were affected by this update.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).

## Connector upgrade guide

<MigrationGuide />
