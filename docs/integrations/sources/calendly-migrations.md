# Calendly Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss
Clearing a stream is destructive: it removes the stream's existing destination data. A re-sync is bounded by your configured `start_date` and by what Calendly still serves. Back up the affected tables before clearing them.
:::

### What changed

- **`scheduled_events`**: The incremental cursor changed from `start_time` to `updated_at`. Each request now uses `min_start_time` set to the configured `start_date`, and incremental syncs emit events whose `updated_at` changed, including upcoming events, cancellations, and reschedules. The existing datetime fields `start_time`, `end_time`, `created_at`, `updated_at`, `cancellation.created_at`, `event_guests[].created_at`, `event_guests[].updated_at`, `event_memberships[].buffered_start_time`, and `event_memberships[].buffered_end_time` now declare `date-time`.
- **`event_invitees`**: Incremental state follows the `scheduled_events` parent, so invitees are re-read for each new or changed event. The existing datetime fields `created_at`, `updated_at`, and `cancellation.created_at` now declare `date-time`; `questions_and_answers[].position` is now an integer.
- **`api_user`**: `created_at` and `updated_at` now declare `date-time`.
- **`event_types`**: `created_at` and `updated_at` now declare `date-time`; `position`, `custom_questions[].position`, and `duration_options[]` are integers.
- **`groups`**: `created_at` and `updated_at` now declare `date-time`.
- **`organization_memberships`**: `created_at`, `updated_at`, `user.created_at`, and `user.updated_at` now declare `date-time`.

### Who must act

If you sync `scheduled_events` or `event_invitees` incrementally, clear both streams after upgrading. The old state uses `start_time`, which may be in the future, and cannot safely resume the new incremental behavior.

If you use Full refresh for these streams, the state change does not require a clear; refresh the source schema. If your destination cannot evolve the changed column types in place, follow the destination notes below.

For the other streams, refresh the source schema. Clear a retyped stream only if your destination cannot change the column type in place.

### Downstream consumers

Update SQL queries, dbt models, dashboards, exports, and object-storage consumers that depend on the retyped columns:

- `scheduled_events`: `start_time`, `end_time`, `created_at`, `updated_at`, `cancellation.created_at`, `event_guests[].created_at`, `event_guests[].updated_at`, `event_memberships[].buffered_start_time`, and `event_memberships[].buffered_end_time`.
- `event_invitees`: `created_at`, `updated_at`, `cancellation.created_at`, and `questions_and_answers[].position`.
- `api_user`: `created_at` and `updated_at`.
- `event_types`: `created_at`, `updated_at`, `position`, `custom_questions[].position`, and `duration_options[]`.
- `groups`: `created_at` and `updated_at`.
- `organization_memberships`: `created_at`, `updated_at`, `user.created_at`, and `user.updated_at`.

### Migration steps

1. Back up the affected destination tables.
2. Refresh the Calendly source schema.
3. If you sync `scheduled_events` or `event_invitees` incrementally, clear both streams.
4. Sync the source and confirm the streams complete successfully.

If you increased `lookback_days` to work around the 0.2.0 incremental-sync limitation, you can set it back to `0`.

### Destination notes

Typed destinations may write values that do not match the new column type as null. S3 Data Lake and GCS Data Lake (Iceberg) cannot evolve string-to-timestamp or number-to-integer columns in place; clear the retyped streams on those destinations before syncing with the refreshed schema.

### Rollback

If you pin back to 0.2.0 after syncing with 1.0.0, clear `scheduled_events` and `event_invitees` again because their state formats differ. Destination columns already typed as timestamps or integers remain that way after rollback.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

<MigrationGuide />
