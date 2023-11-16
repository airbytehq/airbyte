# Pinterest Migration Guide

## Upgrading to 1.0.0

This release updates date-time fields with airbyte_type: timestamp_without_timezone for streams BoardPins, BoardSectionPins, Boards, Catalogs, CatalogFeeds.

Users should:
- Refresh the source schema
- And reset affected streams after upgrading to ensure uninterrupted syncs.
