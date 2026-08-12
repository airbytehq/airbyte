import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Granola Migration Guide

## Upgrading to 0.3.0

The `notes` stream now uses `updated_at` as its incremental cursor field instead of `created_at`. Incremental syncs now include notes edited after their original creation.

### Who is affected

Users syncing the `notes` stream in incremental mode are affected. The stored state from the previous version uses the `created_at` cursor and is incompatible with the new `updated_at` cursor.

### Steps to migrate

1. Update the connector to version 0.3.0.
2. Refresh the source schema.
3. Clear the `notes` stream's data.
4. Re-sync the `notes` stream.

The `detailed_notes` stream remains a full child re-read over all parent notes. It does not use `incremental_dependency` because that option could skip detail updates when a parent cursor does not advance after Granola rewrites a note summary.

## Connector upgrade guide

<MigrationGuide />
