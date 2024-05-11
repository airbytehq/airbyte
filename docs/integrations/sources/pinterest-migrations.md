# Pinterest Migration Guide

## Upgrading to 1.0.0

This release updates date-time fields with airbyte_type: timestamp_without_timezone for streams BoardPins, BoardSectionPins, Boards, Catalogs, CatalogFeeds. Additionally, the stream names AdvertizerReport and AdvertizerTargetingReport have been renamed to AdvertiserReport and AdvertiserTargetingReport, respectively.

To ensure uninterrupted syncs, users should:

- Refresh the source schema
- Reset affected streams
