# MotherDuck

This destination writes data to [MotherDuck](https://motherduck.com), a cloud-based analytics platform built on [DuckDB](https://duckdb.org/). You can also use this destination to write to a local DuckDB file.

This destination implements [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides improved final table structures. Learn more about Destinations V2 in [Typing and Deduping](/platform/using-airbyte/core-concepts/typing-deduping).

## Prerequisites

- A [MotherDuck](https://motherduck.com) account (a free tier is available)
- A [MotherDuck access token](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#creating-an-access-token) for authentication

## Setup guide

### Step 1: Create a MotherDuck access token

<FieldAnchor field="motherduck_api_key">

1. Log in to the [MotherDuck UI](https://app.motherduck.com).
2. Click your organization name in the top left, then click **Settings**.
3. Click **+ Create token**.
4. Name the token and select **Read/Write** as the token type.
5. Copy the token and enter it in the **MotherDuck Access Token** field in Airbyte.

</FieldAnchor>

:::caution

Do not include your access token in the `md:` connection string. This may cause the token to appear in execution logs. Use the **MotherDuck Access Token** field instead.

:::

### Step 2: Configure the destination database

<FieldAnchor field="destination_path">

In the **Destination DB** field, enter the MotherDuck database URI using the `md:` prefix. For example:

- `md:` connects to the default MotherDuck database (`my_db`).
- `md:my_database` connects to a database named `my_database`.

</FieldAnchor>

### Step 3: Configure the schema (optional)

<FieldAnchor field="schema">

In the **Schema Name** field, enter the database schema where Airbyte writes data. If you leave this field blank, data is written to the `main` schema.

</FieldAnchor>

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Output schema

Each table contains the following Airbyte metadata columns in addition to the columns from your source data:

- `_airbyte_raw_id`: A UUID assigned to each record during processing.
- `_airbyte_extracted_at`: A timestamp representing when the record was extracted from the source.
- `_airbyte_meta`: A JSON object containing metadata about the record.

[Data generations](/platform/operator-guides/refreshes#data-generations) are not currently supported.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). The namespace maps to a DuckDB schema in your MotherDuck database.

## Known limitations

- Column names are normalized to lowercase. If your source data contains columns that differ only by case, such as `userId` and `userid`, one of the columns is dropped.

## Working with local DuckDB files

This connector can also write to local DuckDB files. To use a local file, enter a file path instead of a `md:` URI in the **Destination DB** field, for example `/local/destination.duckdb`. For file-based destinations, data is written to `/tmp/airbyte_local` by default. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

If you only need local DuckDB files and don't use MotherDuck, consider the [DuckDB destination](https://docs.airbyte.com/integrations/destinations/duckdb) instead.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| 0.2.2 | 2026-03-17 | [70438](https://github.com/airbytehq/airbyte/pull/70438) | Fix for camelCase columns being `NULL` |
| 0.2.1 | 2026-01-29 | [70999](https://github.com/airbytehq/airbyte/pull/70999) | Fix for empty STRUCTs |
| 0.2.0 | 2026-01-06 | [71063](https://github.com/airbytehq/airbyte/pull/71063) | Upgrade DuckDB to v1.4.2 and duckdb-engine to v0.17.0 |
| 0.1.26 | 2025-10-21 | [68338](https://github.com/airbytehq/airbyte/pull/68338) | Update dependencies |
| 0.1.25 | 2025-10-14 | [67952](https://github.com/airbytehq/airbyte/pull/67952) | Update dependencies |
| 0.1.24 | 2025-10-07 | [66822](https://github.com/airbytehq/airbyte/pull/66822) | Update dependencies |
| 0.1.23 | 2025-08-08 | [64161](https://github.com/airbytehq/airbyte/pull/64161) | feat: allow null values in primary key fields. Primary keys are no longer declared as table constraints. |
| 0.1.22 | 2025-07-22 | [63714](https://github.com/airbytehq/airbyte/pull/63714) | fix(destination-motherduck): handle special characters in stream name when creating tables |
| 0.1.21 | 2025-07-22 | [63709](https://github.com/airbytehq/airbyte/pull/63709) | fix: resolve error "Can't find the home directory at '/nonexistent'" [#63710](https://github.com/airbytehq/airbyte/issues/63710) |
| 0.1.20 | 2025-07-06 | [62133](https://github.com/airbytehq/airbyte/pull/62133) | fix: when `primary_key` is not defined in the catalog, use `source_defined_primary_key` if available |
| n/a    | 2025-06-27 | [48673](https://github.com/airbytehq/airbyte/pull/48673) | Update dependencies |
| 0.1.19 | 2025-05-25 | [60905](https://github.com/airbytehq/airbyte/pull/60905) | Allow unicode characters in database/table names |
| 0.1.18 | 2025-03-01 | [54737](https://github.com/airbytehq/airbyte/pull/54737) | Update airbyte-cdk to ^6.0.0 in destination-motherduck |
| 0.1.17 | 2024-12-26 | [50425](https://github.com/airbytehq/airbyte/pull/50425) | Fix bug overwrite write method not saving all batches |
| 0.1.16 | 2024-12-06 | [48562](https://github.com/airbytehq/airbyte/pull/48562) | Improved handling of config parameters during SQL engine creation. |
| 0.1.15 | 2024-11-07 | [48405](https://github.com/airbytehq/airbyte/pull/48405) | Updated docs and hovertext for schema, api key, and database name. |
| 0.1.14 | 2024-10-30 | [48006](https://github.com/airbytehq/airbyte/pull/48006) | Fix bug in \_flush_buffer, explicitly register dataframe before inserting |
| 0.1.13 | 2024-10-30 | [47969](https://github.com/airbytehq/airbyte/pull/47969) | Preserve Platform-generated id in state messages. |
| 0.1.12 | 2024-10-30 | [47987](https://github.com/airbytehq/airbyte/pull/47987) | Disable PyPi publish. |
| 0.1.11 | 2024-10-30 | [47979](https://github.com/airbytehq/airbyte/pull/47979) | Rename package. |
| 0.1.10 | 2024-10-29 | [47958](https://github.com/airbytehq/airbyte/pull/47958) | Add state counts and other fixes. |
| 0.1.9 | 2024-10-29 | [47950](https://github.com/airbytehq/airbyte/pull/47950) | Fix bug: add double quotes to column names that are reserved keywords. |
| 0.1.8 | 2024-10-29 | [47952](https://github.com/airbytehq/airbyte/pull/47952) | Fix: Add max batch size for loads. |
| 0.1.7 | 2024-10-29 | [47706](https://github.com/airbytehq/airbyte/pull/47706) | Fix bug: incorrect column names were used to create new stream table when using multiple streams. |
| 0.1.6 | 2024-10-29 | [47821](https://github.com/airbytehq/airbyte/pull/47821) | Update dependencies |
| 0.1.5 | 2024-10-28 | [47694](https://github.com/airbytehq/airbyte/pull/47694) | Resolve write failures, move processor classes into the connector. |
| 0.1.4 | 2024-10-28 | [47688](https://github.com/airbytehq/airbyte/pull/47688) | Use new destination table name format, explicitly insert PyArrow table columns by name and add debug info for column mismatches. |
| 0.1.3 | 2024-10-23 | [47315](https://github.com/airbytehq/airbyte/pull/47315) | Fix bug causing MotherDuck API key to not be correctly passed to the engine. |
| 0.1.2 | 2024-10-23 | [47315](https://github.com/airbytehq/airbyte/pull/47315) | Use `saas_only` mode during connection check to reduce ram usage. |
| 0.1.1 | 2024-10-23 | [47312](https://github.com/airbytehq/airbyte/pull/47312) | Fix: generate new unique destination ID |
| 0.1.0 | 2024-10-23 | [46904](https://github.com/airbytehq/airbyte/pull/46904) | New MotherDuck destination |

</details>
