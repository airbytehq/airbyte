# MotherDuck

## Overview

[DuckDB](https://duckdb.org/) is an in-process SQL OLAP database management system and this destination is meant to use locally if you have multiple smaller sources such as GitHub repos, some social media and local CSVs or files you want to run analytics workloads on. This destination writes data to the [MotherDuck](https://motherduck.com) service, or to a file on the _local_ filesystem on the host running Airbyte.

For file-based DBs, data is written to `/tmp/airbyte_local` by default. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

## Destinations V2

This destination implements [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2), which provides improved final table structures. It's a new version of the existing DuckDB destination and works both with DuckDB and MotherDuck.

Learn more about what's new in Destinations V2 [here](/using-airbyte/core-concepts/typing-deduping).

## Use with MotherDuck

This DuckDB destination is compatible with [MotherDuck](https://motherduck.com).

### Specifying a MotherDuck Database

To specify a MotherDuck-hosted database as your destination, simply provide your database uri with the normal `md:` database prefix in the `destination_path` configuration option.

:::caution

We do not recommend providing your API token in the `md:` connection string, as this may cause your token to be printed to execution logs. Please use the `MotherDuck API Key` setting instead.

:::

### Authenticating to MotherDuck

<FieldAnchor field="motherduck_api_key">

For authentication, you will use your [MotherDuck Access Token](https://motherduck.com/docs/key-tasks/authenticating-and-connecting-to-motherduck/authenticating-to-motherduck/#creating-an-access-token).

</FieldAnchor>

### Sync Overview

#### Output schema

Each table will contain at least the following columns:

- `_airbyte_raw_id`: a uuid assigned by Airbyte to each event that is processed.
- `_airbyte_extracted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_meta`: a json blob storing metadata about the record.

In addition, columns specified in the [JSON schema](https://docs.airbyte.com/connector-development/schema-reference) will also be created.

#### Features

| Feature                                                                  | Supported |     |
| :----------------------------------------------------------------------- | :-------- | :-- |
| Full Refresh Sync                                                        | Yes       |     |
| Incremental - Append Sync                                                | Yes       |     |
| Incremental - Append + Deduped                                           | Yes       |     |
| [Typing and Deduplication](/using-airbyte/core-concepts/typing-deduping) | Yes       |     |
| [Namespaces](/using-airbyte/core-concepts/namespaces)                    | No        |     |
| [Data Generations](/operator-guides/refreshes#data-generations)          | No        |     |

#### Performance consideration

This integration will be constrained by the speed at which your filesystem accepts writes.

## Working with local DuckDB files

This connector is primarily designed to work with MotherDuck and local DuckDB files for [Destinations V2](/release_notes/upgrading_to_destinations_v2/#what-is-destinations-v2). If you would like to work only with local DuckDB files, you may want to consider using the [DuckDB destination](https://docs.airbyte.com/integrations/destinations/duckdb).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| 0.1.17  | 2024-12-26 | [50425](https://github.com/airbytehq/airbyte/pull/50425) | Fix bug overwrite write method not not saving all batches                                                                      |
| 0.1.16  | 2024-12-06 | [48562](https://github.com/airbytehq/airbyte/pull/48562) | Improved handling of config parameters during SQL engine creation.                                                               |
| 0.1.15  | 2024-11-07 | [48405](https://github.com/airbytehq/airbyte/pull/48405) | Updated docs and hovertext for schema, api key, and database name.                                                               |
| 0.1.14  | 2024-10-30 | [48006](https://github.com/airbytehq/airbyte/pull/48006) | Fix bug in \_flush_buffer, explicitly register dataframe before inserting                                                        |
| 0.1.13  | 2024-10-30 | [47969](https://github.com/airbytehq/airbyte/pull/47969) | Preserve Platform-generated id in state messages.                                                                                |
| 0.1.12  | 2024-10-30 | [47987](https://github.com/airbytehq/airbyte/pull/47987) | Disable PyPi publish.                                                                                                            |
| 0.1.11  | 2024-10-30 | [47979](https://github.com/airbytehq/airbyte/pull/47979) | Rename package.                                                                                                                  |
| 0.1.10  | 2024-10-29 | [47958](https://github.com/airbytehq/airbyte/pull/47958) | Add state counts and other fixes.                                                                                                |
| 0.1.9   | 2024-10-29 | [47950](https://github.com/airbytehq/airbyte/pull/47950) | Fix bug: add double quotes to column names that are reserved keywords.                                                           |
| 0.1.8   | 2024-10-29 | [47952](https://github.com/airbytehq/airbyte/pull/47952) | Fix: Add max batch size for loads.                                                                                               |
| 0.1.7   | 2024-10-29 | [47706](https://github.com/airbytehq/airbyte/pull/47706) | Fix bug: incorrect column names were used to create new stream table when using multiple streams.                                |
| 0.1.6   | 2024-10-29 | [47821](https://github.com/airbytehq/airbyte/pull/47821) | Update dependencies                                                                                                              |
| 0.1.5   | 2024-10-28 | [47694](https://github.com/airbytehq/airbyte/pull/47694) | Resolve write failures, move processor classes into the connector.                                                               |
| 0.1.4   | 2024-10-28 | [47688](https://github.com/airbytehq/airbyte/pull/47688) | Use new destination table name format, explicitly insert PyArrow table columns by name and add debug info for column mismatches. |
| 0.1.3   | 2024-10-23 | [47315](https://github.com/airbytehq/airbyte/pull/47315) | Fix bug causing MotherDuck API key to not be correctly passed to the engine.                                                     |
| 0.1.2   | 2024-10-23 | [47315](https://github.com/airbytehq/airbyte/pull/47315) | Use `saas_only` mode during connection check to reduce ram usage.                                                                |
| 0.1.1   | 2024-10-23 | [47312](https://github.com/airbytehq/airbyte/pull/47312) | Fix: generate new unique destination ID                                                                                          |
| 0.1.0   | 2024-10-23 | [46904](https://github.com/airbytehq/airbyte/pull/46904) | New MotherDuck destination                                                                                                       |

</details>
