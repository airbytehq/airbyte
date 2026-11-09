# YouTube Analytics Migration Guide

## Upgrading to 2.0.0

:::danger Risk of permanent data loss
Before clearing or rebuilding an affected destination stream, take and verify a backup of its existing data. YouTube makes ordinary report files downloadable for 60 days after generation and historical report files for 30 days. Expired history cannot be restored by re-syncing. Do not clear or overwrite historical data until you have a tested plan to preserve and reconcile it with the new numeric schema.
:::

### What changed

Version 2.0.0 corrects the declared types of report metric fields to match YouTube's definitions: counts are now `integer`, and rates and percentages are now `number` (the rates in `channel_province_a3` were previously `integer`). These fields now have numeric schemas and emitted values. Existing destination columns and downstream consumers may require migration; refreshing the source schema alone does not convert historical data. Preserve historical data before any clear or rebuild.

| Stream | Field | Old type | New type |
| --- | --- | --- | --- |
| channel_annotations_a1 | annotation_click_through_rate | string | number |
| channel_annotations_a1 | annotation_close_rate | string | number |
| channel_annotations_a1 | annotation_clickable_impressions | string | integer |
| channel_annotations_a1 | annotation_clicks | string | integer |
| channel_annotations_a1 | annotation_closable_impressions | string | integer |
| channel_annotations_a1 | annotation_closes | string | integer |
| channel_annotations_a1 | annotation_impressions | string | integer |
| channel_cards_a1 | card_click_rate | string | number |
| channel_cards_a1 | card_teaser_click_rate | string | number |
| channel_cards_a1 | card_clicks | string | integer |
| channel_cards_a1 | card_impressions | string | integer |
| channel_cards_a1 | card_teaser_clicks | string | integer |
| channel_cards_a1 | card_teaser_impressions | string | integer |
| channel_demographics_a1 | views_percentage | string | number |
| channel_end_screens_a1 | end_screen_element_click_rate | string | number |
| channel_end_screens_a1 | end_screen_element_clicks | string | integer |
| channel_end_screens_a1 | end_screen_element_impressions | string | integer |
| channel_sharing_service_a1 | shares | string | integer |
| channel_province_a3 | annotation_click_through_rate | integer | number |
| channel_province_a3 | annotation_close_rate | integer | number |
| channel_province_a3 | card_click_rate | integer | number |
| channel_province_a3 | card_teaser_click_rate | integer | number |
| playlist_province_a2 | playlist_saves_added | string | integer |
| playlist_province_a2 | playlist_saves_removed | string | integer |
| playlist_province_a2 | playlist_starts | string | integer |
| playlist_province_a2 | views | string | integer |

### Update downstream consumers

Before resuming production syncs, update SQL views, dbt models, scheduled queries, dashboards, reverse-ETL mappings and exports that depend on the old types of the 26 fields in the table above. Review string parsing and casts for the string-to-numeric fields, and integer assumptions for the four `channel_province_a3` rates. Object-storage and JSON readers must accept numeric values for these fields; in append mode, older string-valued objects may remain alongside new numeric-valued ones. Validate historical and new-data reconciliation and aggregates so replayed records are not double-counted.

### Migration steps

Only connections that sync at least one of these seven streams are affected: `channel_annotations_a1`, `channel_cards_a1`, `channel_demographics_a1`, `channel_end_screens_a1`, `channel_sharing_service_a1`, `channel_province_a3` and `playlist_province_a2`. Connections that select none of them need no migration beyond the upgrade.

For affected connections, refresh the source schema after upgrading so the catalog carries the new types. Refreshing the catalog does not convert data already in your destination. Whether existing columns can be converted in place or the stream must be rebuilt depends on your destination and sync mode, so choose the path below that matches each affected stream.

#### Full refresh | Overwrite

Refresh the source schema and run a sync. The sync already rebuilds the stream's output from the reports YouTube still makes available, so no extra clear is required.

#### Incremental (Append or Append + Deduped)

These streams can hold history older than YouTube's retention window, so preserve it before changing anything:

1. Take a backup of each affected stream's destination table or files, and verify you can read it back.
2. Refresh the source schema and approve the changes. Do not select **Clear affected streams** unless you have completed step 1 and have a plan for step 4.
3. Run a sync and check the affected columns in your destination.
4. If you have to clear or rebuild a stream, restore the older history from your backup, converting the affected fields to the new numeric types, and reconcile it with the data the new sync replays:
   - In **Append** mode, replayed records are added again, so the restored history and the replayed window can contain duplicate rows.
   - In **Append + Deduped** mode, 2.0.0 doesn't change any primary key, so replayed rows replace matching restored rows as long as deduplication is enabled.

If you don't have a tested way to preserve and reconcile the history, stop before clearing and work out a destination-specific plan first.

#### What a clear cannot recover

After a clear, the destination only receives reports YouTube still makes available: files generated in the last 60 days, and historical report files from the last 30 days. Anything older is gone from the destination, even if the next sync succeeds. Starting a fresh reporting job or using an earlier cursor does not recover expired reports.

For the platform steps to upgrade the connector and refresh the schema, see [Connector upgrade guide](#connector-upgrade-guide) at the end of this page.

## Upgrading to 1.0.0

Version 1.0.0 updates the connector to use the latest versions of YouTube's Bulk Reports API in response to YouTube's Shorts view-counting change. YouTube announced the change on March 26, 2025, Shorts view counting changed on March 31, 2025, and the Bulk Reports API was updated on June 30, 2025. See the YouTube API revision history for details.

### What changed

YouTube updated how views are counted for Shorts:

- **For Shorts**: Views now count the number of times a Short starts to play or replay, with no minimum watch time requirement.
- **For videos**: No change to how views are counted.
- **New metric**: A new `engaged_views` column has been added to reports, which reflects the previous view-counting methodology.

As a result of this change, each affected report's version has incremented by one (for example, version a2 to version a3 for channel reports, and a1 to a2 for playlist reports). See the [YouTube API revision history](https://developers.google.com/youtube/reporting/revision_history) for complete details.

**Important**: previous report versions were deprecated on October 31, 2025. You must upgrade to version 1.0.0 to continue syncing YouTube Analytics data.

## New stream names

| Old Stream                    | New Stream                    |
|:------------------------------|:------------------------------|
| channel_basic_a2              | channel_basic_a3              |
| channel_combined_a2           | channel_combined_a3           |
| channel_device_os_a2          | channel_device_os_a3          |
| channel_playback_location_a2  | channel_playback_location_a3  |
| channel_province_a2           | channel_province_a3           |
| channel_subtitles_a2          | channel_subtitles_a3          |
| channel_traffic_source_a2     | channel_traffic_source_a3     |
| playlist_basic_a1             | playlist_basic_a2             |
| playlist_combined_a1          | playlist_combined_a2          |
| playlist_device_os_a1         | playlist_device_os_a2         |
| playlist_playback_location_a1 | playlist_playback_location_a2 |
| playlist_province_a1          | playlist_province_a2          |
| playlist_traffic_source_a1    | playlist_traffic_source_a2    |

## Migration Steps

### Refresh source schemas and clear data

Clearing your data is required for the affected streams to continue syncing successfully. To clear your data for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds,
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Connector upgrade guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

<MigrationGuide />
