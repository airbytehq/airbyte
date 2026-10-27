# Apple Ads Migration Guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

## Upgrading to 2.0.0

:::danger Risk of permanent data loss
Do not clear the report streams unless the steps for your destination below require it. Apple serves daily reports for the last 90 days only, so a clear permanently deletes every report row older than that. Back up the affected tables before you clear any stream.
:::

This release types the date and time fields Apple returns and adds primary keys to the four entity report streams: `campaigns_report_daily`, `adgroups_report_daily`, `keywords_report_daily` and `ads_report_daily`. The values themselves don't change. Only their declared types do. Apple documents `startTime` and `endTime` as UTC.

### What changed

| Stream | Field | Before | After |
| :-- | :-- | :-- | :-- |
| `campaigns`, `adgroups` | `creationTime`, `modificationTime`, `startTime`, `endTime` | string (`endTime` untyped) | timestamp without time zone |
| `keywords`, `ads` | `creationTime`, `modificationTime` | string | timestamp without time zone |
| the four entity report streams | `date`, `granularity[].date` | string | date |
| `campaigns_report_daily`, `keywords_report_daily` | `metadata.modificationTime` | string | timestamp without time zone |
| `adgroups_report_daily` | `metadata.modificationTime`, `metadata.startTime`, `metadata.endTime` | string (`endTime` untyped) | timestamp without time zone |
| `ads_report_daily` | `metadata.creationTime`, `metadata.modificationTime` | string | timestamp without time zone |

New primary keys:

| Stream | Primary key |
| :-- | :-- |
| `campaigns_report_daily` | `campaignId`, `date`, `countryorregion` |
| `adgroups_report_daily` | `adGroupId`, `date`, `countryorregion` |
| `keywords_report_daily` | `keywordId`, `date`, `countryorregion` |
| `ads_report_daily` | `adId`, `date`, `countryorregion` |

Each report request now covers one day, so `date` is the day of the row's metrics, and the End Date (or today) gets its own request. In 1.x, the newest row of each sync could also carry the next day in `granularity`. To avoid double counting in rows synced before the upgrade, flatten `granularity` and deduplicate on the entity ID, `countryorregion` and each entry's `date`, keeping the most recently extracted row.

Report streams also never start more than 89 days back, one day inside Apple's 90-day limit for daily reports. An older Start Date no longer fails the sync.

### Who needs nothing beyond the upgrade

Upgrade before the deadline shown in Airbyte (2026-12-22). After that date, connections that sync these streams on 1.x are disabled until you upgrade.

- Connections that don't sync any of the streams above.
- Entity streams (`campaigns`, `adgroups`, `keywords`, `ads`) in **Full refresh | Overwrite**. The next sync rebuilds them with the new types.
- Warehouse destinations, apart from the exceptions listed below. They convert the columns during the next sync.
- MotherDuck. Existing columns keep their text type and syncs continue.
- Object storage destinations that write JSONL or CSV.

### Steps

1. Upgrade the connector, then refresh the source schema for the connection and save it. Because the report streams' primary key changed, Airbyte may recommend refreshing or clearing them when you save. Save without refreshing or clearing, unless the section for your destination below says otherwise: a refresh that keeps records appends another copy of the last 90 days, and a clear deletes older report rows for good.
2. Follow the section for your destination.
3. Sync.

#### BigQuery, Snowflake, Redshift, Postgres, Databricks, ClickHouse, MS SQL Server

Don't clear. On the next sync, the destination converts the existing top-level columns in place. Fields under `metadata` and `granularity` stay inside their JSON column, so they don't change.

The exception is entity streams in **Full refresh | Append**. The sync fails if a stored value can't be converted. This happens on Postgres for the old untyped `endTime` column of `campaigns` and `adgroups`, and on BigQuery for `ads` timestamps that end in `Z`. For those streams, either switch to **Full refresh | Overwrite**, or back up the table and clear the stream. A clear removes the snapshots you appended, and Apple only serves current objects.

#### S3 Data Lake, GCS Data Lake (Iceberg)

Iceberg can't change a string column to a date or timestamp. Until you clear them, incremental syncs of the report streams fail with `Schema evolution for column ... is not allowed`. Entity streams in **Full refresh | Overwrite** are rebuilt automatically. Entity streams in **Full refresh | Append** fail the same way: switch them to **Full refresh | Overwrite**, or back them up and clear them.

1. Copy each report table with your query engine (for example `CREATE TABLE ... AS SELECT`), or point the connection at a new namespace so the old tables stay as history.
2. Clear the four report streams, or refresh them with records removed. A refresh that retains records still fails.
3. Sync. If you need rows older than 90 days, reload them from the copy and cast `date` to a date.

#### S3, GCS, Azure Blob Storage

New Avro and Parquet files store these fields as date and timestamp types, while older files store strings. Readers that apply one schema to the whole path, such as Glue, Athena or Spark, must handle both types. Alternatively, set a new path for 2.0.0 output. JSONL and CSV output is unchanged. Don't clear the report streams: a clear deletes older files that Apple can't serve again.

#### MotherDuck

No action is needed. Existing columns keep their text type. Entity streams in **Full refresh | Overwrite** switch to the new types on their next sync.

### Primary keys and sync modes

- **Incremental | Append**: the destination ignores primary keys, so the new key changes nothing, as long as you save the refreshed schema without a refresh or clear.
- **Incremental | Append + Deduped** now uses the declared key on the report streams, and switching to it is optional. Deduplication applies to rows synced after the switch. Duplicates already in the table from earlier lookback re-reads stay. Remove them with a one-off query rather than a clear.
- If you set your own primary key on a report stream in 1.x, the declared key replaces it.

### If you skip these steps

- Until you refresh the source schema, the destination keeps the old text columns, unless your connection applies schema changes automatically.
- On Iceberg destinations, report streams and entity streams in **Full refresh | Append** fail on every sync until they're cleared.
- After 2026-12-22, connections that still run 1.x and sync these streams are disabled until you upgrade.
- On Avro and Parquet paths, old and new files have different types for the same fields.

### Downstream

Update any SQL, dbt models, dashboards or exports that treat `date`, `creationTime`, `modificationTime`, `startTime` or `endTime` as text, for example with string comparisons, `SUBSTR`, `LIKE` or concatenation. On Iceberg, Avro and Parquet, `metadata.*Time` and `granularity[].date` are typed too.

### Rolling back

After the first 2.0.0 sync, pinning the connection back to 1.x doesn't restore the old tables. Warehouses convert the columns back to text in their own timestamp format rather than Apple's, and Iceberg syncs fail. Back up before upgrading if you might roll back.

## Upgrading to 1.0.0

This release introduces changes to incremental sync of `adgroups_report_daily` and `keywords_report_daily` streams, changing the stream state from per-partition state to a global state cursor. This change decreases the sync time for these streams.

### Affected streams

- `adgroups_report_daily`
- `keywords_report_daily`

### Migration steps

For the 1.0.0 upgrade only: to clear your data for the `adgroups_report_daily` and `keywords_report_daily` streams, follow the steps below:

1. Select **Connections** in the main nav bar.
   1. Select the connection(s) affected by the update.
2. Select the **Status** tab.
   1. In the **Enabled streams** list, click the three dots on the right side of the affected stream and select **Clear Data**.

After the clear succeeds, trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Connector upgrade guide

For 2.0.0, skip **Clear data from affected streams** in the general steps below. Clear only where the section for your destination in [Upgrading to 2.0.0](#upgrading-to-200) tells you to.

<MigrationGuide />
