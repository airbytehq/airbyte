import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Aircall Migration Guide

## Upgrading to 1.0.0

:::danger Risk of permanent data loss for `calls`
Aircall's API returns only the last six months of calls. Clearing `calls`, or switching it from an append mode to any Overwrite mode, deletes every older call for good: a re-sync can't restore it. Aircall Support can provide a one-time export of older calls. Copy the `calls` table before you do either.
:::

Version 1.0.0 adds primary keys for deduplication, makes `numbers` and `teams` full refresh only, and declares the types the [Aircall API reference](https://developers.aircall.io/api-references/) documents. The values Aircall returns don't change.

### What changed

| Stream | Change |
| :--- | :--- |
| `calls` | New primary key `id`. `contact`, `assigned_to`, `transferred_by` and `transferred_to` change from string to object. Inside the existing object and array columns, `number.priority` is declared as an integer and `user.created_at`, `number.created_at`, `teams[].created_at`, `comments[].posted_by.created_at` and `tags[].tagged_by.created_at` as date-times. |
| `contacts` | New primary key `id`. |
| `webhooks` | Primary key changes from `id` to `webhook_id`, the UUID Aircall now uses to identify webhooks. |
| `numbers` | Full refresh only; incremental sync is removed. `priority` changes from string to integer. |
| `teams` | Full refresh only; incremental sync is removed. `users[].created_at` is declared as a date-time inside the `users` column. |
| `users` | `created_at` changes from string to timestamp. |

`company` still has no primary key, because Aircall returns a single company object with no identifier.

Neither the `numbers` nor the `teams` endpoint filters by update time, so their incremental mode re-read every record on every sync and added duplicates of every number and team.

### Who needs to act

Connections that sync none of the six streams above need no action. All other connections refresh the source schema. Whether anything else is needed depends on the destination and the sync mode, as the steps below say.

### Before you upgrade

On **ClickHouse**, converting an existing `users.created_at` column to a timestamp sets its values to null. If `users` uses `Full Refresh | Append`, copy the `users` table or switch the stream to `Full Refresh | Overwrite` before the first 1.0.0 sync. If the connection propagates field changes automatically, do this before you upgrade.

### Steps

1. Upgrade the connector to 1.0.0.
2. In the connection, open **Schema** and select **Refresh source schema**, then review and save. If Airbyte recommends clearing or refreshing streams when you save, save without clearing `calls` when it uses an append mode: a refresh re-reads six months of calls into the table. Connections that propagate field changes automatically apply the type changes on their own, but pause until you review the schema if a deduplicated stream's primary key changes.
3. `numbers` and `teams` that used an Incremental mode (after the refresh they can show `Full Refresh | Append`): select `Full Refresh | Overwrite` or `Full Refresh | Overwrite + Deduped`. The next sync replaces the table, duplicates included, and drops numbers and teams that were deleted in Aircall: copy the table first if you need them. If `numbers` or `teams` already used `Full Refresh | Append` to keep snapshots, you can leave them there; switching them to an Overwrite mode deletes the earlier snapshots.
4. Streams in `Full Refresh | Overwrite` or `Full Refresh | Overwrite + Deduped`: nothing else to do. The next sync rebuilds the table with the new keys and types. On MSSQL the columns are changed in place instead; see the MSSQL note below.
5. `calls` in any append mode (`Full Refresh | Append`, `Incremental | Append` or `Incremental | Append + Deduped`): the table can hold calls older than six months. Follow [If you keep an append-mode calls table](#if-you-keep-an-append-mode-calls-table) for your destination.
6. To deduplicate `calls` with the new key, select `Incremental | Append + Deduped`: it keeps every row. Don't switch an append-mode `calls` table to an Overwrite mode (see the warning above). For `contacts` and `webhooks`, `Full Refresh | Overwrite + Deduped` deduplicates; on an append-mode table it also drops records that were deleted in Aircall.
7. On S3 Data Lake or GCS Data Lake, which reject these type changes in place: copy and then clear `numbers` and `users` if they use `Full Refresh | Append`, because the clear deletes the snapshots of earlier syncs; and copy and clear `calls` before you switch it to `Incremental | Append + Deduped`.
8. Run a sync.

### If you keep an append-mode calls table

Before 1.0.0, the Bulk CDK destinations wrote the four `calls` fields that become objects as JSON text.

- **Snowflake**: the schema refresh changes these columns from `VARCHAR` to `OBJECT`, which Snowflake can't do for the existing text, so the next sync fails (in `Incremental | Append + Deduped`, at the end of the sync). Before the first 1.0.0 sync, either convert each of the four columns yourself (try it on a copy first: `CREATE TABLE CALLS_COPY CLONE CALLS`), or copy the table and clear `calls`. To convert `CONTACT`, for example:

  ```sql
  ALTER TABLE CALLS ADD COLUMN CONTACT_OBJECT OBJECT;
  UPDATE CALLS SET CONTACT_OBJECT = TRY_PARSE_JSON(CONTACT)::OBJECT;
  ALTER TABLE CALLS DROP COLUMN CONTACT;
  ALTER TABLE CALLS RENAME COLUMN CONTACT_OBJECT TO CONTACT;
  ```

- **BigQuery** and **Postgres**: the columns become `JSON` and `JSONB`, and existing rows keep the old values as JSON strings. Convert them in place after the first 1.0.0 sync, for each of the four columns:

  ```sql
  -- BigQuery
  UPDATE calls SET contact = SAFE.PARSE_JSON(JSON_VALUE(contact)) WHERE JSON_TYPE(contact) = 'string';
  -- Postgres
  UPDATE calls SET contact = (contact #>> '{}')::jsonb WHERE jsonb_typeof(contact) = 'string';
  ```

- **Redshift**, and **ClickHouse** with the JSON type: existing values are parsed into `SUPER` or `JSON`; no action.
- **MSSQL**: the four columns become `TEXT`, changed in place in every sync mode. Cast them to `NVARCHAR(MAX)` in queries that use `JSON_VALUE`, `=`, `GROUP BY` or `ORDER BY`.
- **MotherDuck**: append modes keep the existing text columns, so old rows hold DuckDB struct text and new rows JSON text. `Full Refresh | Overwrite` rebuilds them as `JSON` and `users.created_at` as a timestamp.
- **Databricks**, **ClickHouse** without the JSON type, **S3 Data Lake**, **GCS Data Lake**, and CSV or JSONL files on **S3**, **GCS** or **Azure Blob Storage**: no change for these four fields.
- Avro or Parquet files on **S3**, **GCS** or **Azure Blob Storage**: new files use integer and timestamp types for `priority` and the `created_at` fields above. In append modes, update table definitions that read the whole prefix, or copy and clear.

### Update downstream queries

- `users.created_at` is a timestamp column on typed destinations (on MotherDuck, after an Overwrite rebuild). Queries that treat it as text (string comparisons, `LIKE`, `SUBSTR`, parsing) must treat it as a timestamp.
- `calls.contact`, `calls.assigned_to`, `calls.transferred_by` and `calls.transferred_to` are JSON or object columns on BigQuery, Snowflake, Redshift, Postgres, ClickHouse with the JSON type, and MotherDuck after a rebuild; queries must read them as objects.
- `numbers.priority` is an integer column: compare it with `0` and `1`, not `'0'` and `'1'`. The nested `calls.number.priority` and `created_at` values already arrived as numbers and ISO text inside JSON columns; only Avro and Parquet files change their types.
- Models that join `webhooks` on `id` should join on `webhook_id`.
- Models that remove duplicate `numbers` or `teams` rows from append-mode tables can drop that step once the tables are rebuilt.

### Roll back

Pinning the connector back to 0.6.0 after this migration reverses the type changes and drops the new keys: refresh the schema again, and copy `calls` before any clear. On S3 Data Lake and GCS Data Lake, append-mode `numbers` and `users` tables then reject the reverse changes, so copy and clear them. On other destinations, `users.created_at` comes back as text in the warehouse's timestamp format, not the original ISO text.

## Connector upgrade guide

<MigrationGuide />
