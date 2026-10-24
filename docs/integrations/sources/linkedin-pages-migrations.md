# Linkedin Pages Migration Guide

## Upgrading to 2.0.0

:::danger Risk of permanent data loss
Follow the steps below to preserve historical data. If you don't, you risk permanent and irreversible loss of data in your destination.
:::

### What changed

All six streams now declare primary keys:

| Stream | Primary key |
| --- | --- |
| `organization_lookup` | `id` |
| `follower_statistics` | `organizationalEntity` |
| `share_statistics` | `organizationalEntity` |
| `total_follower_count` | `organizationalEntity` |
| `follower_statistics_time_bound` | [`organizationalEntity`, `timeRangeStart`] |
| `share_statistics_time_bound` | [`organizationalEntity`, `timeRangeStart`] |

The declared type changes from `number` to `integer` for:

- `timeRangeStart` and `timeRangeEnd` in `follower_statistics_time_bound` and `share_statistics_time_bound`.
- `created.time`, `lastModified.time`, and `id` in `organization_lookup`.

Values are unchanged; the timestamps remain epoch milliseconds.

Two fields are added:

- `organizationalEntity` on `total_follower_count`, with the value `urn:li:organization:<org_id>`.
- `date` on both time-bound streams, formatted as `YYYY-MM-DD` for the UTC day of `timeRangeStart`.

The cursor (`timeRangeEnd`) and saved state are unchanged.

### Why

The streams had no declared keys, so **Append + Deduped** was unavailable and re-syncs in append mode could duplicate rows. Timestamp fields were declared as generic numbers, so typed destinations could store epoch-millisecond values as floating-point columns.

### Who must act

Every connection syncing any of the six streams above must refresh its source schema and follow the steps below.

### Steps

1. Upgrade the connector to version 2.0.0.
2. Refresh the source schema by selecting **Connection → Schema → Refresh source schema**, then review and accept the changes.
3. For `organization_lookup`, `follower_statistics`, `share_statistics`, and `total_follower_count`, clearing or refreshing is safe. These are full-refresh streams containing the current snapshot; the next sync re-pulls their available records.
4. Before changing `follower_statistics_time_bound` or `share_statistics_time_bound`, back up their destination tables. LinkedIn only returns time-bound statistics for the last 12 months, so clearing and re-syncing permanently loses any older rows. Prefer [**Refresh and retain records**](/platform/operator-guides/refreshes) if your destination supports it. Only clear these streams if you accept losing older history; see the [clear guide](/platform/operator-guides/clear).
5. Optionally, switch the time-bound streams to **Incremental | Append + Deduped**.

### Downstream

Update SQL, dbt models, dashboards, or other consumers that cast `follower_statistics_time_bound.timeRangeStart`, `follower_statistics_time_bound.timeRangeEnd`, `share_statistics_time_bound.timeRangeStart`, `share_statistics_time_bound.timeRangeEnd`, `organization_lookup.created.time`, `organization_lookup.lastModified.time`, or `organization_lookup.id` from floating-point values to use integer columns. Queries on `total_follower_count` can now join on `organizationalEntity`.

## Upgrading to 1.0.7

- 2 new streams have been added which support time bound incremental sync. They need additional fields `start_date` and `time_granularity_type` to be defined in the config to work. `time_granularity_type` has a default value of `DAY` set, and `start_date` has a default value set 1 year prior to the current date.

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Connector upgrade guide

<MigrationGuide />
