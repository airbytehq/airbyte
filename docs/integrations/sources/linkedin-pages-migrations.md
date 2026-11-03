# LinkedIn Pages Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

:::danger Risk of permanent data loss
LinkedIn only returns time-bound statistics for the last 12 months. Back up the `follower_statistics_time_bound` and `share_statistics_time_bound` tables before you clear these streams or refresh them with **Remove records**. Rows older than 12 months cannot be synced again.
:::

### What changed

**Type changes.** These fields change from `number` to `integer`. The values stay the same epoch milliseconds.

| Stream | Fields |
| --- | --- |
| `follower_statistics_time_bound` | `timeRangeStart`, `timeRangeEnd` |
| `share_statistics_time_bound` | `timeRangeStart`, `timeRangeEnd` |
| `organization_lookup` | `id`, `created.time`, `lastModified.time` |

**Primary keys.** The six streams that existed before 1.3.0 now declare primary keys. The streams added in 1.3.0 are unchanged.

| Stream | Primary key |
| --- | --- |
| `organization_lookup` | `id` |
| `follower_statistics` | `organizationalEntity` |
| `share_statistics` | `organizationalEntity` |
| `total_follower_count` | `organizationalEntity` |
| `follower_statistics_time_bound` | `organizationalEntity`, `timeRangeStart`, `timeRangeEnd` |
| `share_statistics_time_bound` | `organizationalEntity`, `timeRangeStart`, `timeRangeEnd` |

**New fields.**

- `organizationalEntity` on `total_follower_count`, with the value `urn:li:organization:<Organization ID>`.
- `date` on `follower_statistics_time_bound` and `share_statistics_time_bound`, and on `page_statistics_time_bound` from 1.3.0: the UTC date of `timeRangeStart`, formatted as `YYYY-MM-DD`.

The cursor (`timeRangeEnd`) and saved state do not change.

### Who must act

- **No action:** connections that sync none of `organization_lookup`, `follower_statistics_time_bound` and `share_statistics_time_bound`. The new keys and fields on the other streams need nothing.
- **Everyone else:** follow the steps below. Most destinations only need the schema refresh in step 2. Upgrade before the deadline shown in Airbyte (2026-12-22): after that date, connections that sync the affected streams on 1.x are disabled until you upgrade.

### Steps

1. Upgrade the connector to 2.0.0.
2. In the connection, open **Schema**, select **Refresh source schema**, then review and save the changes. Because primary keys changed, Airbyte may recommend refreshing or clearing streams when you save. Save without refreshing or clearing, unless your destination's row in step 3 says otherwise: a refresh that keeps records appends a second copy of the last 12 months to the time-bound streams, and a clear deletes rows older than 12 months for good.
3. Find your destination below. "Affected streams" means `organization_lookup`, `follower_statistics_time_bound` and `share_statistics_time_bound`.

   | Destination | What the next sync does | Action |
   | --- | --- | --- |
   | BigQuery, Snowflake, Databricks, ClickHouse, MS SQL Server | Converts the existing columns to integer in place. The values are whole numbers, so nothing is lost. | None. |
   | Postgres, Redshift | Converts the existing columns in place, but the sync fails if a view depends on one of them. | Drop the dependent views before the sync and recreate them after it. On Redshift, the **Drop tables with CASCADE** option also works, but it deletes those views. |
   | MotherDuck, DuckDB | Keeps the existing decimal columns and writes the integer values into them. | None. |
   | S3 Data Lake, GCS Data Lake | Iceberg cannot change a double column to a long. Incremental and append syncs of the affected streams fail with `Schema evolution for column ... between double and long is not allowed`. **Refresh and retain records** fails the same way. **Full Refresh \| Overwrite** syncs replace the column and succeed. | `organization_lookup` in **Full Refresh \| Overwrite**: none. Time-bound streams: back up the tables, set the Start Date as in step 4, then refresh the streams with **Remove records** or [clear](/platform/operator-guides/clear) them. |
   | S3, GCS, Azure Blob Storage with Avro or Parquet | Writes new files that declare these fields as `long`. Older files declare them as `double`. | Make readers such as Glue, Athena or Spark accept both types, or cast. Do not clear: it deletes the files that hold older history. |
   | S3, GCS, Azure Blob Storage with JSONL or CSV | Files carry no column types. | None. |

4. **Start Date.** Before you clear a time-bound stream or refresh it with **Remove records**, leave **Start Date** empty or set it to 12 months ago. The connector never requests more than 12 months back, so an earlier date cannot restore older rows, and a later date restores even less.
5. **Optional: deduplicate.** You can now switch the time-bound streams to **Incremental | Append + Deduped**. The switch only merges rows synced after it, so duplicate rows already in the table stay. Remove them with SQL on the new key, or refresh with **Remove records** and accept losing rows older than 12 months. Do not use **Refresh and retain records** while the stream is in **Incremental | Append**: it appends a second copy of the last 12 months.

### If you skip these steps

- BigQuery, Snowflake, Databricks, ClickHouse, MS SQL Server and MotherDuck: nothing else happens. History stays in place.
- Postgres and Redshift with dependent views: syncs of the affected streams fail until you drop the views.
- S3 Data Lake and GCS Data Lake: syncs of the affected streams keep failing until you refresh them with **Remove records** or clear them.
- Avro and Parquet: new and old files under the same stream path declare different types for these fields.
- If you don't refresh the source schema and your connection doesn't propagate schema changes automatically, the destination keeps the old types, and the new fields and keys don't appear.
- After 2026-12-22, connections that still run 1.x and sync the affected streams are disabled until you upgrade.

### Downstream

- Update SQL, dbt models, dashboards and exports that read `timeRangeStart` and `timeRangeEnd` in `follower_statistics_time_bound` and `share_statistics_time_bound`, or `id`, `created.time` and `lastModified.time` in `organization_lookup`, as floating-point or decimal values. Where the destination converts them, they are now integer columns.
- Update table definitions for readers of S3 Data Lake, GCS Data Lake, and Avro or Parquet files.
- If you changed **Time Granularity Type** in the past, the time-bound tables hold both day and month rows. They have separate keys. Filter on `timeRangeEnd - timeRangeStart` (86400000 for a day) before you aggregate. The first sync after a clear can also include a partial first month when 12 months ago or the Start Date falls inside a month.
- `total_follower_count` rows written before 2.0.0 have no `organizationalEntity`.

### Rollback

Pinning back to 1.x declares these fields as `number` again. BigQuery, Snowflake, Redshift, Postgres, Databricks, ClickHouse and MS SQL Server convert the columns back on the next sync, and Postgres and Redshift again fail while views depend on them. S3 Data Lake and GCS Data Lake cannot change a long column back to double, so a rollback there needs another **Remove records** refresh or clear, with the same 12-month limit.

## Upgrading to 1.0.7

- 2 new streams have been added which support time bound incremental sync. They need additional fields `start_date` and `time_granularity_type` to be defined in the config to work. `time_granularity_type` has a default value of `DAY` set, and `start_date` has a default value set 1 year prior to the current date.

## Connector upgrade guide

For 2.0.0, skip **Clear data from affected streams** in the general steps below. Clear only where your destination's row in [Upgrading to 2.0.0](#upgrading-to-200) tells you to.

<MigrationGuide />
