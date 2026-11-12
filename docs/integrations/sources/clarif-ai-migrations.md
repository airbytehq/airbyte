# Clarifai Migration Guide

## Upgrading to 1.0.0

The `modified_at` field in `applications`, `datasets`, and `models` is now emitted with
six fractional digits (microseconds). For example, `2026-10-14T09:41:55.568082659Z` becomes
`2026-10-14T09:41:55.568082Z`. Digits beyond microseconds are truncated.
This fixes incremental state that previously stayed at `start_date` when Clarifai returned
nanosecond timestamps. Updates within one microsecond now share a timestamp, but the connector
continues reading and emitting every available record without a new timestamp filter.

Field names, types, primary keys (`id`), and state structure do not change.
Existing global and per-application state remains readable. Other streams are unaffected.

### Migration steps

1. Review SQL views, dbt models, BI dashboards, exports, and other consumers that compare,
   order, or parse `modified_at` for the three affected streams. Update exact-string comparisons
   and assumptions about nine fractional digits; sub-microsecond ordering is no longer available
   in newly emitted values.
2. Upgrade the connector to 1.0.0. No source-schema refresh, state reset, or stream clear is required.
   Connections that have not upgraded by the deadline are disabled so consumers can be reviewed first.
3. Run a sync and verify that incremental state advances to the newest `modified_at` returned by
   Clarifai (for datasets and models, within each application partition). The list endpoints
   still reread available records, so Append modes continue to receive repeated IDs.
4. Check the destination behavior for your sync mode:

   | Sync mode | Effect on existing data |
   | --- | --- |
   | Full Refresh / Overwrite | The next sync rebuilds the stream using currently available records with normalized timestamps. |
   | Full Refresh / Append or Incremental / Append | Existing rows retain their original precision; new rows are appended with six digits. |
   | Incremental / Append + Deduped | IDs still match existing rows, but destination cursor comparisons can retain an older, higher-precision value for the same update. Later updates can replace it. |

If historical timestamp strings must be uniform, back up destination data and assess a separate
refresh or downstream conversion. A clear is optional and deletes existing stream data:
records deleted from Clarifai or no longer available from the API cannot be restored by a resync.
Do not clear streams merely to advance state.
