# YouTube Analytics Migration Guide

## Upgrading to 1.0.0

The YouTube Analytics Bulk Reports API made changes one of which is  create new report versions for each report that includes views, which is the majority of the reports. Each affected report's version has incremented by one, such as version a2 to version a3. See [here](https://developers.google.com/youtube/reporting/revision_history#june-24,-2025) for more details.

## New stream names

| Old Stream                                       | New Stream |
| :------                                          | :--------- |
| channel_basic_a2                                 | channel_basic_a3 |
| channel_combined_a2                              | channel_combined_a3 |
| channel_device_os_a2                             | channel_device_os_a3 |
| channel_playback_location_a2                     | channel_playback_location_a3 |
| channel_province_a2                              | channel_province_a3 |
| channel_subtitles_a2                             | channel_subtitles_a3 |
| channel_traffic_source_a2                        | channel_traffic_source_a3 |
| playlist_basic_a1                                | playlist_basic_a2 |
| playlist_combined_a1                             | playlist_combined_a2 |
| playlist_device_os_a1                            | playlist_device_os_a2 |
| playlist_playback_location_a1                    | playlist_playback_location_a2 |
| playlist_province_a1                             | playlist_province_a2 |
| playlist_traffic_source_a1                       | playlist_traffic_source_a2 |

## Migration Steps

### Refresh source schemas and clear data

Clearing your data is required for the affected streams in order to continue syncing successfully. To clear your data 
for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds, 
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).


<MigrationGuide />
