# Google Ads Migration Guide

## Upgrading to 2.0.0

This release includes enhancements to the default schemas and updates to stream names so user can easier match it to Google Ads resource. Users should refresh the source schema and reset affected streams after upgrading to ensure uninterrupted syncs.

## Upgrading to 1.0.0

This release introduced fixes to the creation of custom query schemas. For instance, the field ad_group_ad.ad.final_urls in the custom query has had its type changed from `{"type": "string"}` to `{"type": ["null", "array"], "items": {"type": "string"}}`. Users should refresh the source schema and reset affected streams after upgrading to ensure uninterrupted syncs.