# Clarifai Migration Guide

## Upgrading to 1.0.0

The `modified_at` field in `applications`, `datasets`, and `models` is now emitted with six
fractional digits. For example, `2026-10-14T09:41:55.568082659Z` becomes
`2026-10-14T09:41:55.568082Z`. Millisecond and whole-second timestamps are padded to six
fractional digits. Missing, null, and empty values are not normalized. Other streams are unchanged.

This fixes successful incremental syncs whose saved state stayed at `start_date` because
nanosecond timestamps could not be parsed. The cursor remains `modified_at`, primary keys
remain `id`, and the existing flat applications state and per-app datasets/models state remain readable.

### Before upgrading

1. Review SQL views, dbt models, dashboards, exports, and joins that compare `modified_at`
   strings or rely on nanosecond precision in these three streams. Adapt them to microsecond
   precision. Values that differ only below one microsecond now compare equal.
2. Preserve any existing nanosecond values you need for auditing in a separate table or export.
   New output cannot retain their sub-microsecond precision; a later sync may replace existing
   values when using deduplication or overwrite.
3. Upgrade using the connector upgrade guide below, then run a sync and verify that the
   applications cursor and each app's datasets/models cursor advance to the newest timestamps.

No source schema refresh, state reset, or stream clear is required. Do not clear these streams
to apply this fix: clearing deletes destination data, and records deleted upstream may not be recoverable.
Connections that do not select these streams need no downstream changes.

### Destination impact

- **Incremental | Append + Deduped:** The unchanged `id` primary keys still identify the same
  records. Newly synced versions carry microsecond timestamps. Review consumers that use
  the timestamp itself as a key or tie-breaker.
- **Incremental | Append** and **Full Refresh | Append:** Existing rows are retained and new
  rows are appended, so old nanosecond strings and new microsecond strings can coexist.
  The list endpoints still replay records; this release does not remove existing duplicates.
- **Full Refresh | Overwrite:** The next sync replaces current output with microsecond
  timestamps. Back up any sub-microsecond values you need before that sync.

Connections still on the old major version are disabled at the upgrade deadline rather than
automatically upgraded, allowing downstream precision-dependent consumers to be reviewed first.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

<MigrationGuide />
