import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Google Ads Migration Guide

## Upgrading to 6.0.0

:::danger Risk of permanent data loss
**Pay careful attention to this migration guide to avoid permanent data loss in your destination**.
:::

Beginning June 1, 2026, the [Google Ads Data Retention Policy](https://support.google.com/google-ads/answer/15188209) makes hourly, daily, and weekly reporting data available for 37 months. Connector version 6.0.0 limits Google Ads incremental report streams to this 37-month granular data retention window. Airbyte no longer queries data older than 37 months for:

1. Built-in streams that use `segments.date`:
   1. `account_performance_report`
   2. `ad_group`
   3. `ad_group_ad`
   4. `ad_group_ad_legacy`
   5. `ad_group_bidding_strategy`
   6. `campaign`
   7. `campaign_bidding_strategy`
   8. `campaign_budget`
   9. `click_view`
   10. `customer`
   11. `display_keyword_view`
   12. `geographic_view`
   13. `geographic_view_with_metrics`
   14. `keyword_view`
   15. `shopping_performance_view`
   16. `topic_view`
   17. `user_location_view`
2. Custom query streams that use `segments.date`.

The connector clamps configured date ranges to fit inside the 37-month retention window. If your configured `start_date` is more than 37 months ago, the connector uses 37 months ago as the effective start. If both `start_date` and `end_date` fall outside the retention window, the connector emits no records for the configured historical range. Review your `start_date` and `end_date` settings before upgrading; you may need to adjust them if the connection was configured to sync only historical data outside the retained window.

### Action required

You don't need to refresh the source schema or reset affected streams for this change. Before upgrading, review whether you need to preserve synced Google Ads report data older than 37 months. **If you don't do this, you risk permanent data loss in your destination**.

- **Full Refresh | Overwrite sync mode**: destination data is rebuilt from the connector's current output. After this update, records older than 37 months are no longer emitted and can be overwritten or removed from the destination. Store any historical data older than 37 months before upgrading if you need to keep it.
- **Incremental | Append or Incremental | Append + Deduped sync modes**: existing deduplicated destination records older than 37 months are not overwritten by this connector change because the sync mode preserves prior records. This preservation is due to the selected sync mode; after upgrading, the connector can no longer sync those older records.

<MigrationGuide />

## Upgrading to 5.0.0

This release combines two breaking changes:

1. The Google Ads API is upgraded from Version 20 to Version 23 (see key changes below).
2. The nullable `bidding_strategy.id` field is removed from primary keys. See the table below for new primary keys.

### Google Ads API v23 changes

Key changes include:

- New `segments.ad_network_type` support for Performance Max campaigns (channel-level reporting)
- Renamed deprecated video metrics to TrueView equivalents
- Removed `CallAd` and `CallAdInfo` fields from `ad_group_ad` schema
- Renamed campaign date fields to datetime equivalents
- Removed `lead_form_only` field from `DemandGenMultiAssetAdInfo`
- Removed aggregate asset performance label metrics

The following field renames and removals affect built-in stream schemas:

| Stream | Previous field name | New field name |
|---|---|---|
| `account_performance_report` | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| `account_performance_report` | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| `account_performance_report` | `metrics.video_views` | `metrics.video_trueview_views` |
| `ad_group_ad` | `ad_group_ad.ad.call_ad.*` / `CallAdInfo` fields | Removed |
| `ad_group_ad_legacy` | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| `ad_group_ad_legacy` | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| `ad_group_ad_legacy` | `metrics.video_views` | `metrics.video_trueview_views` |
| `campaign` | `campaign.start_date` | `campaign.start_date_time` |
| `campaign` | `campaign.end_date` | `campaign.end_date_time` |
| `campaign` | `metrics.video_views` | `metrics.video_trueview_views` |
| `campaign_budget` | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| `campaign_budget` | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| `campaign_budget` | `metrics.video_views` | `metrics.video_trueview_views` |
| `display_keyword_view` | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| `display_keyword_view` | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| `display_keyword_view` | `metrics.video_views` | `metrics.video_trueview_views` |
| `geographic_view_with_metrics` | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| `geographic_view_with_metrics` | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| `geographic_view_with_metrics` | `metrics.video_views` | `metrics.video_trueview_views` |
| `topic_view` | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| `topic_view` | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| `topic_view` | `metrics.video_views` | `metrics.video_trueview_views` |
| `user_location_view` | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| `user_location_view` | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| `user_location_view` | `metrics.video_views` | `metrics.video_trueview_views` |

The following fields were also removed in v23 and may affect custom queries (`custom_queries_array`), even though they are not used in built-in streams:

- `campaign.url_expansion_opt_out`
- `ad_group_ad.ad.demand_gen_multi_asset_ad.lead_form_only`
- `asset_group_asset.performance_label`

For custom queries, the stream may fail if a field was removed or renamed during the API update. Users with custom queries that reference any of the renamed or removed fields above must update their queries accordingly.
You can use the [Query Builder](https://developers.google.com/google-ads/api/fields/v23/query_validator) to validate your custom queries.

### Primary key change for bidding strategy streams

The `bidding_strategy.id` field is nullable in the Google Ads API, meaning it can return `null` values. Including a nullable field in the primary key caused sync failures for destinations that enforce non-null primary key constraints, such as the Iceberg destination.

| Stream | Old primary key | New primary key |
|---|---|---|
| `campaign_bidding_strategy` | `campaign.id`, `bidding_strategy.id`, `segments.date` | `campaign.id`, `segments.date` |
| `ad_group_bidding_strategy` | `ad_group.id`, `bidding_strategy.id`, `segments.date` | `ad_group.id`, `segments.date` |

Users syncing the `campaign_bidding_strategy` or `ad_group_bidding_strategy` streams are affected.

### Action required

After upgrading, refresh the source schema and clear data for the affected streams to ensure uninterrupted syncs.

<MigrationGuide />

## Upgrading to 4.0.0

This release upgrades the Google Ads API from Version 18 to Version 20 which causes the following changes in the schemas:

| Stream                   | Current field name                                                | New field name                                                                                                  |
|--------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| campaign                 | campaign.dynamic_search_ads_setting.feeds                         | This field has been deleted                                                                                     |
| user_interests           | user_interest.availabilities                                      | Updated advertisingChannelSubType enum for the Video channel: removed VIDEO_OUTSTREAM and added YOUTUBE_AUDIO.  |

For custom queries, the stream may fail if a field was removed during the API update. Additionally, some field values may have changed, such as `user_interest.availabilities`.
You can use the [Query Builder](https://developers.google.com/google-ads/api/fields/v20/query_validator) to validate your custom queries.

Users should:

- Refresh the source schema
- Reset affected streams after upgrading to ensure uninterrupted syncs.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).


## Upgrading to 3.0.0

This release upgrades the Google Ads API from Version 13 to Version 15 which causes the following changes in the schemas:

| Stream                     | Current field name                                                         | New field name                                                           |
| -------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| ad_listing_group_criterion | ad_group_criterion.listing_group.case_value.product_bidding_category.id    | ad_group_criterion.listing_group.case_value.product_category.category_id |
| ad_listing_group_criterion | ad_group_criterion.listing_group.case_value.product_bidding_category.level | ad_group_criterion.listing_group.case_value.product_category.level       |
| shopping_performance_view  | segments.product_bidding_category_level1                                   | segments.product_category_level1                                         |
| shopping_performance_view  | segments.product_bidding_category_level2                                   | segments.product_category_level2                                         |
| shopping_performance_view  | segments.product_bidding_category_level3                                   | segments.product_category_level3                                         |
| shopping_performance_view  | segments.product_bidding_category_level4                                   | segments.product_category_level4                                         |
| shopping_performance_view  | segments.product_bidding_category_level5                                   | segments.product_category_level5                                         |
| campaign                   | campaign.shopping_setting.sales_country                                    | This field has been deleted                                              |

Users should:

- Refresh the source schema
- Reset affected streams after upgrading to ensure uninterrupted syncs.

### Refresh affected schemas and reset data

1. Select **Connections** in the main navbar.
   1. Select the connection(s) affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

```note
Any detected schema changes will be listed for your review.
```

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

```note
Depending on destination type you may not be prompted to reset your data.
```

4. Select **Save connection**.

```note
This will reset the data in your destination and initiate a fresh sync.
```

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Upgrading to 2.0.0

This release updates the Source Google Ads connector so that its default streams and stream names match the related resources in [Google Ads API](https://developers.google.com/google-ads/api/fields/v14/ad_group_ad).

Users should:

- Refresh the source schema
- And reset affected streams after upgrading to ensure uninterrupted syncs.

## Upgrading to 1.0.0

This release introduced fixes to the creation of custom query schemas. For instance, the field ad_group_ad.ad.final_urls in the custom query has had its type changed from `{"type": "string"}` to `{"type": ["null", "array"], "items": {"type": "string"}}`. Users should refresh the source schema and reset affected streams after upgrading to ensure uninterrupted syncs.
