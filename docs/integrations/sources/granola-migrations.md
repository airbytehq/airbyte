import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Granola Migration Guide

## Upgrading to 0.2.0

The `notes` stream now uses `updated_at` as the incremental cursor field instead of `created_at`.

### What changed

Previously, the connector used `created_at` to track incremental sync progress. This meant that notes edited after their initial creation were not captured in subsequent syncs. The cursor field has been changed to `updated_at` so that both new and edited notes are included during incremental syncs.

Additionally, the `updated_at` field has been added to the `notes` stream schema, the `detailed_notes` substream now uses `incremental_dependency` to only fetch details for notes in the current incremental window, and concurrency and rate limiting have been added to respect the API's 5 requests/second limit.

### Who is affected

Users syncing the `notes` stream in incremental mode are affected by this change. The stored state from the previous version references the `created_at` cursor, which is incompatible with the new `updated_at` cursor.

### Steps to migrate

1. Update the connector to version 0.2.0.
2. Reset the `notes` stream to clear the old state. This triggers a full re-sync of the stream.
3. If you sync `detailed_notes`, reset that stream as well, since it depends on `notes`.

## Connector upgrade guide

<MigrationGuide />
