# MotherDuck

## Overview

The MotherDuck destination writes data to [MotherDuck](https://motherduck.com), a cloud-based analytics service built on [DuckDB](https://duckdb.org/). You can also use this destination to write to a local DuckDB file on the host running Airbyte.

This destination implements [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides improved final table structures. It works with both MotherDuck and local DuckDB files. Learn more about Destinations V2 in the [Typing and Deduping](/platform/using-airbyte/core-concepts/typing-deduping) documentation.

:::info

[Data generations](/platform/operator-guides/refreshes#data-generations) are not currently supported.

:::

## Prerequisites

To use this destination, you need:

- A [MotherDuck account](https://motherduck.com) with a valid [access token](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#creating-an-access-token), or a local filesystem path for a DuckDB file.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Configuration

<FieldAnchor field="motherduck_api_key">

### MotherDuck API key

Your [MotherDuck access token](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#creating-an-access-token). Required for connecting to MotherDuck. You can create a token in the MotherDuck UI under **Settings**.

</FieldAnchor>

<FieldAnchor field="destination_path">

### Destination database

The path to a `.duckdb` file or a MotherDuck database URI using the `md:` prefix. Defaults to `md:`, which connects to the default MotherDuck database (`my_db`).

Examples: `md:`, `md:my_db`, `/local/destination.duckdb`

:::caution

Do not include your API token in the `md:` connection string. This may cause your token to appear in execution logs. Use the **MotherDuck API Key** field instead.

:::

</FieldAnchor>

<FieldAnchor field="schema">

### Schema name

The database schema to write data into. Defaults to `main` if not specified.

</FieldAnchor>

## Output schema

Each destination table contains the following columns in addition to columns from the source data:

| Column | Description |
| :--- | :--- |
| `_airbyte_raw_id` | A UUID assigned by Airbyte to each processed record. |
| `_airbyte_extracted_at` | A timestamp representing when the record was extracted from the source. |
| `_airbyte_meta` | A JSON object containing metadata about the record. |

## Column name normalization

This destination normalizes column names from the source data before writing them to the destination table. The normalization rules are:

- ASCII letters are converted to lowercase.
- Whitespace is replaced with underscores.
- Unicode letters and numbers are preserved.
- An underscore prefix is added if the name starts with a digit.
- Other special characters are replaced with underscores.

For example, a source column named `firstName` becomes `firstname` in the destination, and `User Name` becomes `user_name`.

If two source columns produce the same name after normalization (for example, `userid` and `userId` both normalize to `userid`), the record is skipped and a warning is logged. Ensure that source column names are unique after normalization.

:::tip

If you previously observed `NULL` values in columns with mixed-case names, upgrade to version 0.2.2 or later and run a full refresh on affected streams.

:::

## Working with local DuckDB files

This connector is primarily designed to work with MotherDuck. If you only need to work with local DuckDB files, consider using the [DuckDB destination](https://docs.airbyte.com/integrations/destinations/duckdb).

For local file-based databases, data is written to `/tmp/airbyte_local` by default. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces). The namespace maps to a DuckDB schema.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| 0.2.2 | 2026-03-17 | [70438](https://github.com/airbytehq/airbyte/pull/70438) | Fix for camelCase columns being `NULL` |
| 0.2.1 | 2025-12-19 | [70999](https://github.com/airbytehq/airbyte/pull/70999) | Fix for empty STRUCTs |
| 0.2.0 | 2025-12-01 | [70221](https://github.com/airbytehq/airbyte/pull/70221) | Upgrade DuckDB to v1.4.2 and duckdb-engine to v0.17.0 |
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
