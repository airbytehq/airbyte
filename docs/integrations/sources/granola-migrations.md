# Granola Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 changes the `notes` stream's incremental cursor from `created_at` to `updated_at`, so notes edited after a sync are replicated again instead of requiring a full refresh. Records in `notes` now include the `updated_at` field.

This is a breaking change for existing connections:

- Cursor state written by earlier versions is keyed on `created_at`, which the new `updated_at` cursor ignores. The first sync after upgrading re-reads every note updated since your configured `start_date`, which can produce duplicate records in destinations that sync in append mode.
- `start_date` now bounds when notes were last *updated*, not when they were created. The first sync after upgrading may therefore read notes created before your start date that were updated after it.

To avoid duplicates and pick up the new cursor, [reset or refresh](/platform/operator-guides/refreshes) the `notes`, `detailed_notes`, and `note_transcripts` streams after upgrading. `detailed_notes` and `note_transcripts` read their partitions from `notes`, so they must be reset alongside it.
