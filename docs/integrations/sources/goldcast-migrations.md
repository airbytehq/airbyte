import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Goldcast Migration Guide

## Upgrading to 1.0.0

:::note
This change only affects you if you sync the `event_members` stream to S3 or GCS in **Avro or Parquet** format and read fields inside `props`. Database and data-lake destinations (BigQuery, Snowflake, Redshift, Postgres, ClickHouse, MSSQL, S3 Data Lake, GCS Data Lake) already store `props` as a complete JSON value and are not affected - no action is needed there.
:::

`props` carries Goldcast **registration form fields**, which every workspace defines for itself. Until now the schema enumerated a fixed list of eleven of them (`city`, `solutions`, `tag_source`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `tag_country`, `tag_form_type`, `revenue_type`, `contact_job_title`). On S3 and GCS in Avro or Parquet format, `props` was written as a record with exactly those eleven fields, and any other registration field was dropped silently - it did not even appear in `_airbyte_meta.changes[]`. Destinations that store objects as JSON (databases and data lakes) always kept every field.

`props` is now a schemaless object. Avro and Parquet files carry it as a JSON string, so **every** field **every** workspace defines is preserved, and no schema change is needed when a workspace adds one. The trade-off is that `props` is delivered as a JSON string rather than a set of nested columns.

### What to do

- **Database or data-lake destination**: nothing. The `props` column keeps the same type and content.
- **S3 or GCS in Avro/Parquet, Full Refresh | Overwrite**: refresh the source schema (steps below). The next sync rewrites `event_members` with `props` as a JSON string; a reset is optional.
- **S3 or GCS in Avro/Parquet, Full Refresh | Append**: refresh the source schema. Then either keep the existing files and handle both shapes of `props` in your readers, or reset the stream to get one consistent shape - read the warning first.

:::danger Risk of permanent data loss
Resetting an `event_members` stream synced in **Full Refresh | Append** deletes every earlier snapshot in the destination. Goldcast only returns the current registrants, so those point-in-time snapshots cannot be re-fetched. Copy or archive the stream's prefix before resetting.
:::

### Update downstream consumers

Readers of the Avro or Parquet files that access `props.<field>` as a nested column must extract the value from the JSON string instead:

- Athena / Trino: `json_extract_scalar(props, '$.city')`
- Spark: `get_json_object(props, '$.city')`
- DuckDB: `props->>'$.city'`

Glue or Athena table definitions that declare `props` as a struct need the column redefined as `string`.

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.
3. Select **Save changes** at the bottom of the page.
   1. Check **Reset affected streams** only if you decided to reset the stream (see above).
4. Select **Save connection**.

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear).

## Connector upgrade guide

<MigrationGuide />
