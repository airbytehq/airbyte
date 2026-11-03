import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Calendly Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream deletes its destination data. Calendly doesn't return deleted events and invitees, so their rows aren't restored, and in append modes a clear also removes every earlier version of each record. Back up the affected tables before you clear anything, and clear only what the destination notes below ask for.
:::

### What changed

- **`scheduled_events`**: the incremental cursor changed from `start_time` to `updated_at`. Every sync requests events from your start date, and incremental syncs emit the events whose `updated_at` changed, including upcoming events, cancellations and reschedules. Events updated while a sync runs are left out of that sync, with their invitees, in every sync mode, and the next sync emits them; in Full refresh | Overwrite their rows are missing until then. The existing datetime fields `start_time`, `end_time`, `created_at`, `updated_at`, `cancellation.created_at`, `event_guests[].created_at`, `event_guests[].updated_at`, `event_memberships[].buffered_start_time` and `event_memberships[].buffered_end_time` now declare `date-time`.
- **`event_invitees`**: its state follows `scheduled_events`, and all invitees of each new or changed event are read again. `created_at`, `updated_at` and `cancellation.created_at` now declare `date-time`; `questions_and_answers[].position` is now an integer.
- **`api_user`**: `created_at` and `updated_at` now declare `date-time`.
- **`event_types`**: `created_at` and `updated_at` now declare `date-time`; `position`, `custom_questions[].position` and the `duration_options` items are integers.
- **`groups`**: `created_at` and `updated_at` now declare `date-time`.
- **`organization_memberships`**: `created_at`, `updated_at`, `user.created_at` and `user.updated_at` now declare `date-time`.

### Who must act

You don't need to clear `scheduled_events` or `event_invitees` for the cursor change. Version 1.0.0 ignores the old `start_time` state, so the first sync after the upgrade reads every event that starts on or after your start date with all of its invitees, including the bookings and cancellations that 0.2.0 missed. In Incremental | Append + Deduped mode these rows replace the existing ones by `uri`; in Incremental | Append mode the first sync appends one more copy of each event and invitee. If you moved your start date later after the first sync, move it back first.

Every connection must refresh the source schema so the new column types apply. Whether you also need to clear a stream depends on your destination; see the destination notes.

If you raised `lookback_days` to work around the 0.2.0 incremental limitation, set it back to `0`: a larger value now re-emits every event updated in that window and reads its invitees again on every sync. If you switched `scheduled_events` and `event_invitees` to Full refresh for the same reason, you can switch them back to Incremental | Append + Deduped; Full refresh reads the invitees of every event on every sync.

### Destination notes

The retyped top-level columns are `created_at` and `updated_at` on all six streams, `start_time` and `end_time` on `scheduled_events`, and `position` on `event_types`. Nested fields (for example `cancellation.created_at` or `questions_and_answers[].position`) and `event_types.duration_options` stay JSON in warehouse destinations and change only in S3 Data Lake, GCS Data Lake and typed file formats.

- **BigQuery, Snowflake, Redshift, Databricks and Postgres** convert the existing text and decimal columns to timestamps and integers in place. Calendly's values match the new types, so no clear is needed.
- **Postgres and Redshift**: drop every view that reads a retyped column, including `SELECT *` views, before the first 1.0.0 sync, and recreate it afterwards. Postgres can't change the type of a column a view depends on, and Redshift can't drop it unless **Drop tables and columns with CASCADE** is on (which drops those views), so the sync fails.
- **ClickHouse** changes the column types in place but turns the existing timestamp text into empty values. For any of the six streams synced in an append mode, and for `event_types` in Incremental | Append + Deduped mode, back up the table and clear the stream before the first 1.0.0 sync. `scheduled_events` and `event_invitees` in Incremental | Append + Deduped mode are rebuilt by the first sync's full re-read. Full refresh | Overwrite streams are rebuilt and need nothing.
- **S3 Data Lake and GCS Data Lake** can't change these column types in place, including `event_types.position` and `event_types.duration_options`. For streams synced in an append or incremental mode, every sync of the connection fails with `Schema evolution for column ... is not allowed` until you clear them, so clear those streams when you refresh the schema. Full refresh | Overwrite streams are rebuilt on the next sync.
- **S3 and GCS with Avro or Parquet** write the new types in new files; files written earlier keep the old types, so readers that combine old and new files must handle both.
- **MotherDuck and DuckDB** keep the existing column types until a clear or a Full refresh | Overwrite sync recreates the table. **JSONL and CSV** outputs don't change.

### Downstream consumers

Update SQL queries, dbt models, dashboards and exports that read the retyped top-level columns listed above, and object-storage consumers that read the nested fields in Avro or Parquet.

### Migration steps

1. Back up the affected destination tables.
2. On Postgres or Redshift, drop the views that read retyped columns.
3. Upgrade the connector and refresh the source schema.
4. Clear only the streams the destination notes list for your destination and sync mode.
5. Sync, confirm the streams complete, and recreate any views you dropped.

### Rollback

Rolling back to 0.2.0 brings back its incremental defect: depending on the saved state it either reads again from your start date or resumes from an old upcoming-event cursor, and either way its incremental syncs stall. If you roll back, sync `scheduled_events` and `event_invitees` in Full refresh while you stay on 0.2.0. Don't refresh the schema after rolling back on a destination that already converted the columns, or typed destinations convert the timestamps and integers back to text and decimals in a different text format.

## Connector upgrade guide

<MigrationGuide />
