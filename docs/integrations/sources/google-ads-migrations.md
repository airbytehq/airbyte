# Google Ads Migration Guide

## Upgrading to 5.0.0

This release upgrades the Google Ads API from Version 20 to Version 23. Key changes include:

- New `segments.ad_network_type` support for Performance Max campaigns (channel-level reporting)
- Renamed deprecated video metrics to TrueView equivalents
- Removed `CallAd` and `CallAdInfo` fields from `ad_group_ad` schema
- Renamed campaign date fields to datetime equivalents
- Removed `lead_form_only` field from `DemandGenMultiAssetAdInfo`
- Removed aggregate asset performance label metrics

The following field renames and removals affect built-in stream schemas:

| Stream | Previous field name | New field name |
|---|---|---|
| Various report streams | `metrics.video_views` | `metrics.video_trueview_views` |
| Various report streams | `metrics.average_cpv` | `metrics.trueview_average_cpv` |
| Various report streams | `metrics.video_view_rate` | `metrics.video_trueview_view_rate` |
| campaign | `campaign.start_date` | `campaign.start_date_time` |
| campaign | `campaign.end_date` | `campaign.end_date_time` |
| ad_group_ad | `CallAd` / `CallAdInfo` fields | Removed |

The following fields were also removed in v23 and may affect custom queries (`custom_queries_array`), even though they are not used in built-in streams:

- `campaign.url_expansion_opt_out`
- `ad_group_ad.ad.demand_gen_multi_asset_ad.lead_form_only`
- `asset_group_asset.performance_label`

For custom queries, the stream may fail if a field was removed or renamed during the API update. Users with custom queries that reference any of the renamed or removed fields above must update their queries accordingly.
You can use the [Query Builder](https://developers.google.com/google-ads/api/fields/v23/query_validator) to validate your custom queries.

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
