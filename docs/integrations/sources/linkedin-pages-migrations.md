# Linkedin Pages Migration Guide

## Upgrading to 2.0.0

Version 2.0.0 declares primary keys for all six streams, types epoch-millisecond timestamp fields (`timeRangeStart`, `timeRangeEnd`, `created.time`, and `lastModified.time`) and `organization_lookup.id` as integers, adds an `organizationalEntity` field to `total_follower_count`, and adds a `date` field to both time-bound streams. These primary keys let destinations deduplicate records, and the corrected types ensure timestamp and identifier values use the expected destination types.

After upgrading, use **Refresh → Clear data** for the affected streams so the destination recreates their tables with the new keys and types. See the [refresh guide](/platform/operator-guides/refreshes) and [clear data guide](/platform/operator-guides/clear) for details. Optionally, change the time-bound streams to **Incremental | Append + Deduped** to deduplicate records using the new primary keys. The cursor fields and saved state are unchanged.

## Upgrading to 1.0.7

- 2 new streams have been added which support time bound incremental sync. They need additional fields `start_date` and `time_granularity_type` to be defined in the config to work. `time_granularity_type` has a default value of `DAY` set, and `start_date` has a default value set 1 year prior to the current date.