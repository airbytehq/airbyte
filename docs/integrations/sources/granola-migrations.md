# Granola Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 1.0.0

Version 1.0.0 changes the `notes` stream's incremental cursor from `created_at` to `updated_at`, so notes edited after a sync are replicated again instead of requiring a full refresh. Records in `notes` now include the `updated_at` field.

This is a breaking change for existing connections:

- Cursor state written by earlier versions is keyed on `created_at`, which the new `updated_at` cursor ignores. The first sync after upgrading re-reads every note updated since your configured `start_date`, which can produce duplicate records in destinations that sync in append mode.
- `start_date` now bounds when notes were last *updated*, not when they were created. The first sync after upgrading may therefore read notes created before your start date that were updated after it.
- The first sync after upgrading reads every note updated since your `start_date` in a single pass. If it fails partway through, the next attempt restarts from `start_date`.

### Who needs to act

If your connection doesn't propagate schema changes automatically, [refresh the source schema](/platform/using-airbyte/schema-change-management#manually-refresh-the-source-schema) after upgrading so it picks up the new `updated_at` column and cursor. Then:

- `notes` in **Incremental | Append + Deduped** or **Full Refresh | Overwrite**: no action is needed. The first sync re-reads your notes and the destination keeps one row per note, now with its latest edits.
- `notes` in **Incremental | Append**: the first sync appends a second copy of every note updated since your start date. From then on, each edit to a note appends a new row. If you want one row per note, switch the stream to **Append + Deduped**. To remove the one-time duplicates, [refresh the stream and remove records](/platform/operator-guides/refreshes). Read the warning below first.

:::danger
Clearing the `notes` stream, or refreshing it with **Remove records**, deletes the existing rows from your destination. The next sync can only bring back notes Granola still returns: notes you deleted or unshared, notes your API key can no longer read, and notes last updated before your start date are gone for good. If you left **Start Date** empty, it's a rolling two-year window. Snapshot the `notes` table first if you need that history.
:::

### Update downstream models

If you sync `notes` in **Incremental | Append**, your destination now holds more than one row per note. Each edit adds a new row, and each sync repeats the most recently updated note, because the connector re-reads the stored cursor's last second so it doesn't miss changes made in that second. Models, dashboards, and file consumers that assume one row per `id` should keep the row with the latest `updated_at` for each `id`.

### Other streams

`detailed_notes` and `note_transcripts` don't need any action. They have no cursor state and re-read every note updated since your `start_date` on every sync. After upgrading, they also include notes created before your `start_date` that were updated after it.

## Connector upgrade guide

:::note
The general steps below end by clearing the affected streams. That step doesn't apply to this upgrade: refresh the source schema, then follow [Who needs to act](#who-needs-to-act) instead of clearing `notes`.
:::

<MigrationGuide />
