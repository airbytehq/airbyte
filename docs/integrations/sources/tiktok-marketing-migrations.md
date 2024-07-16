# TikTok Marketing Migration Guide

## Upgrading to 4.0.0

We're continuously striving to enhance the quality and reliability of our connectors at Airbyte. As part of our commitment to delivering exceptional service, we are transitioning source TikTok Marketing from the Python Connector Development Kit (CDK) to our innovative low-code framework. This is part of a strategic move to streamline many processes across connectors, bolstering maintainability and freeing us to focus more of our efforts on improving the performance and features of our evolving platform and growing catalog. However, due to differences between the Python and low-code CDKs, this migration constitutes a breaking change.

We’ve evolved and standardized how state is managed for incremental streams that are nested within a parent stream. This change impacts how individual states are tracked and stored for each partition, using a more structured approach to ensure the most granular and flexible state management. 

This change will affect the following streams:
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

See `Clearing data` to update your connection.

Schema changes for `advertiser_ids` stream. 
Type of advertiser_id field was changed from integer to string to use actual data types as it's declared in API docs. Users will need to refresh stream schema.

See `Refresh schemas` to update your connection.

## Migration Steps

### Refresh schemas

Refreshing `advertiser_ids` schema is required in order to continue syncing `advertiser_ids` stream data. To refresh schema follow the steps below:

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

### Clearing data 

Clearing your data is required in order to continue syncing affected stream from list above successfully. To clear your data for the streams, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the impacted stream and select **Clear Data**.
3. Do the same steps from 1-2.1 for all streams in your connection that were affected by this update. 

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](https://docs.airbyte.com/operator-guides/reset).


