# MotherDuck

## Overview

The MotherDuck destination writes each Airbyte stream to a table in a [MotherDuck](https://motherduck.com/) database. It connects through the DuckDB client and supports MotherDuck-hosted databases and local DuckDB files.

<!-- env:cloud -->

:::caution

Local DuckDB files aren't persistent in Airbyte Cloud. Use a MotherDuck-hosted database in Airbyte Cloud.

:::

<!-- /env:cloud -->

## Prerequisites

To write to MotherDuck, you need:

- A MotherDuck account.
- A [Read/Write access token](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#creating-an-access-token). Read Scaling tokens are read-only and don't work with this destination.
- The name of a MotherDuck database that the token's account can write to.

For automated production workloads, you can use a [MotherDuck service account](https://motherduck.com/docs/key-tasks/service-accounts-guide/create-and-configure-service-accounts/) with a Read/Write token. An organization Admin must create and configure service accounts.

## Set up the destination

1. In MotherDuck, open your organization settings and select **Create token**.
2. Select **Read/Write**, configure an expiration if needed, and copy the token.
3. In Airbyte, create a MotherDuck destination.
4. Enter the following values:

   <FieldAnchor field="motherduck_api_key">

   - **MotherDuck Access Token**: Enter the Read/Write token you created.

   </FieldAnchor>

   <FieldAnchor field="destination_path">

   - **Destination DB**: Enter `md:<database-name>`, for example `md:analytics`. Enter `md:` to use MotherDuck's default `my_db` database.

   Don't include the token in the connection string. Tokens in connection strings might appear in execution logs.

   </FieldAnchor>

   <FieldAnchor field="schema">

   - **Schema Name**: Enter the schema where Airbyte creates destination tables. The default is `main`.

   </FieldAnchor>

5. Select **Set up destination** and wait for the connection test to complete.

## Destinations V2

This destination implements [Destinations V2](/release_notes/self-managed/upgrading_to_destinations_v2/#what-is-destinations-v2), which writes source fields directly to typed destination columns.

Learn more in the [Typing and deduping guide](/platform/using-airbyte/core-concepts/typing-deduping).

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | Yes |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Output schema

Each table will contain at least the following columns:

- `_airbyte_raw_id`: A UUID assigned by Airbyte to each record.
- `_airbyte_extracted_at`: The time Airbyte extracted the record from the source.
- `_airbyte_meta`: A JSON object containing record metadata.

The destination also creates typed columns for fields in each stream's [JSON schema](/platform/connector-development/schema-reference).

Table and column names are normalized before Airbyte creates them:

- Letters are converted to lowercase.
- Whitespace and most special characters are replaced with underscores.
- Unicode letters and numbers are preserved.
- Names that start with a digit receive an underscore prefix.

## Working with local DuckDB files

<!-- env:oss -->

In Self-Managed Airbyte, you can enter a local `.duckdb` file path for **Destination DB**. Airbyte normalizes the path under `/local`, which maps to the host directory configured by `LOCAL_ROOT`. The default host directory is `/tmp/airbyte_local`.

For example, `/local/destination.duckdb` maps to `/tmp/airbyte_local/destination.duckdb` with the default `LOCAL_ROOT`.

If you only need local DuckDB files, consider using the [DuckDB destination](/integrations/destinations/duckdb).

<!-- /env:oss -->

## Limitations

- The connector writes all selected streams to the configured **Schema Name**. It doesn't map source namespaces to separate MotherDuck schemas.
- Stream names must be unique after normalization, including streams from different source namespaces.
- Field names in a record must be unique after normalization. If fields collide, such as `userId` and `userid`, the connector skips the record.
- [Data generations](/platform/operator-guides/refreshes#data-generations) aren't supported.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--- | :----------- | :------ |
| 0.2.4 | 2026-07-14 | [81511](https://github.com/airbytehq/airbyte/pull/81511) | Fix silent data loss on multi-stream syncs by no longer discarding other streams' buffered records when one stream is flushed |
| 0.2.3 | 2026-03-31 | [75645](https://github.com/airbytehq/airbyte/pull/75645) | Bump version to force registry update for supportLevel change to certified |
| 0.2.2 | 2026-03-17 | [70438](https://github.com/airbytehq/airbyte/pull/70438) | Fix for camelCase columns being `NULL` |
| 0.2.1 | 2026-01-29 | [70999](https://github.com/airbytehq/airbyte/pull/70999) | Fix for empty STRUCTs |
| 0.2.0 | 2026-01-07 | [71063](https://github.com/airbytehq/airbyte/pull/71063) | Upgrade DuckDB to v1.4.2 and duckdb-engine to v0.17.0 |
| 0.1.26 | 2025-10-21 | [68338](https://github.com/airbytehq/airbyte/pull/68338) | Update dependencies |
| 0.1.25 | 2025-10-14 | [67952](https://github.com/airbytehq/airbyte/pull/67952) | Update dependencies |
| 0.1.24 | 2025-10-07 | [66822](https://github.com/airbytehq/airbyte/pull/66822) | Update dependencies |
| 0.1.23 | 2025-08-08 | [64161](https://github.com/airbytehq/airbyte/pull/64161) | feat: allow null values in primary key fields. Primary keys are no longer declared as table constraints. |
| 0.1.22 | 2025-07-22 | [63714](https://github.com/airbytehq/airbyte/pull/63714) | fix(destination-motherduck): handle special characters in stream name when creating tables |
| 0.1.21 | 2025-07-22 | [63709](https://github.com/airbytehq/airbyte/pull/63709) | fix: resolve error "Can't find the home directory at '/nonexistent'" [#63710](https://github.com/airbytehq/airbyte/issues/63710) |
| 0.1.20 | 2025-07-07 | [62133](https://github.com/airbytehq/airbyte/pull/62133) | fix: when `primary_key` is not defined in the catalog, use `source_defined_primary_key` if available |
| n/a | 2025-06-26 | [48673](https://github.com/airbytehq/airbyte/pull/48673) | Update dependencies |
| 0.1.19 | 2025-05-28 | [60906](https://github.com/airbytehq/airbyte/pull/60906) | Allow unicode characters in database/table names |
| 0.1.18 | 2025-03-01 | [54737](https://github.com/airbytehq/airbyte/pull/54737) | Update airbyte-cdk to ^6.0.0 in destination-motherduck |
| 0.1.17 | 2024-12-26 | [50425](https://github.com/airbytehq/airbyte/pull/50425) | Fix bug overwrite write method not saving all batches |
| 0.1.16 | 2024-12-06 | [48562](https://github.com/airbytehq/airbyte/pull/48562) | Improved handling of config parameters during SQL engine creation. |
| 0.1.15 | 2024-11-09 | [48405](https://github.com/airbytehq/airbyte/pull/48405) | Updated docs and hovertext for schema, api key, and database name. |
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
