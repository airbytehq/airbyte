# Google Ads Migration Guide

## Upgrading to 3.0.0

This release upgrades the Google Ads API to version 15 which causes the following changes in the schemas:

| Stream                     | Current field name                                                         | New field name                                                           |
|----------------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------|
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
- And reset affected streams after upgrading to ensure uninterrupted syncs.

## Upgrading to 2.0.0

This release updates the Source Google Ads connector so that its default streams and stream names match the related resources in [Google Ads API](https://developers.google.com/google-ads/api/fields/v14/ad_group_ad).

Users should:
- Refresh the source schema
- And reset affected streams after upgrading to ensure uninterrupted syncs.

## Upgrading to 1.0.0

This release introduced fixes to the creation of custom query schemas. For instance, the field ad_group_ad.ad.final_urls in the custom query has had its type changed from `{"type": "string"}` to `{"type": ["null", "array"], "items": {"type": "string"}}`. Users should refresh the source schema and reset affected streams after upgrading to ensure uninterrupted syncs.