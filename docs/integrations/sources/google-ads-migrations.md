# Google Ads Migration Guide

## Upgrading to 2.0.0

This release updates the Source Google Ads connector so that its default streams and stream names match the related resources in [Google Ads API](https://developers.google.com/google-ads/api/fields/v14/ad_group_ad).

Users should:
- Refresh the source schema
- And reset affected streams after upgrading to ensure uninterrupted syncs.

## Upgrading to 1.0.0

This release introduced fixes to the creation of custom query schemas. For instance, the field ad_group_ad.ad.final_urls in the custom query has had its type changed from `{"type": "string"}` to `{"type": ["null", "array"], "items": {"type": "string"}}`. Users should refresh the source schema and reset affected streams after upgrading to ensure uninterrupted syncs.