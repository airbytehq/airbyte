# DuckDB

<!-- env:cloud -->

:::caution

Local file-based DBs will not work in Airbyte Cloud or Kubernetes. Please use MotherDuck when running in Airbyte Cloud.

:::

<!-- /env:cloud -->

## Overview

[DuckDB](https://duckdb.org/) is an in-process SQL OLAP database management system and this destination is meant to use locally if you have multiple smaller sources such as GitHub repos, some social media and local CSVs or files you want to run analytics workloads on. This destination writes data to the [MotherDuck](https://motherduck.com) service, or to a file on the _local_ filesystem on the host running Airbyte.

For file-based DBs, data is written to `/tmp/airbyte_local` by default. To change this location, modify the `LOCAL_ROOT` environment variable for Airbyte.

## Use with MotherDuck

This DuckDB destination is compatible with [MotherDuck](https://motherduck.com).

### Specifying a MotherDuck Database

To specify a MotherDuck-hosted database as your destination, simply provide your database uri with the normal `md:` database prefix in the `destination_path` configuration option.

:::caution

We do not recommend providing your API token in the `md:` connection string, as this may cause your token to be printed to execution logs. Please use the `MotherDuck API Key` setting instead.

:::

### Authenticating to MotherDuck

For authentication, you can provide your [MotherDuck Service Credential](https://motherduck.com/docs/authenticating-to-motherduck/#syntax) as the `motherduck_api_key` configuration option.

### Sync Overview

#### Output schema

Each table will contain 3 columns:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing with the event data.

### Normalization

If you set [Normalization](https://docs.airbyte.com/understanding-airbyte/basic-normalization/), source data will be normalized to a tabular form. Let's say you have a source such as GitHub with nested JSONs; the Normalization ensures you end up with tables and columns. Suppose you have a many-to-many relationship between the users and commits. Normalization will create separate tables for it. The end state is the [third normal form](https://en.wikipedia.org/wiki/Third_normal_form) (3NF).

#### Features

| Feature                        | Supported |     |
| :----------------------------- | :-------- | :-- |
| Full Refresh Sync              | Yes       |     |
| Incremental - Append Sync      | Yes       |     |
| Incremental - Append + Deduped | No        |     |
| Namespaces                     | No        |     |

#### Performance consideration

This integration will be constrained by the speed at which your filesystem accepts writes.

<!-- env:oss -->

## Getting Started with Local Database Files

The `destination_path` will always start with `/local` whether it is specified by the user or not. Any directory nesting within local will be mapped onto the local mount.

By default, the `LOCAL_ROOT` env variable in the `.env` file is set `/tmp/airbyte_local`.

The local mount is mounted by Docker onto `LOCAL_ROOT`. This means the `/local` is substituted by `/tmp/airbyte_local` by default.

:::caution

Please make sure that Docker Desktop has access to `/tmp` (and `/private` on a MacOS, as /tmp has a symlink that points to /private. It will not work otherwise). You allow it with "File sharing" in `Settings -> Resources -> File sharing -> add the one or two above folder` and hit the "Apply & restart" button.

:::

### Example:

- If `destination_path` is set to `/local/destination.duckdb`
- the local mount is using the `/tmp/airbyte_local` default
- then all data will be written to `/tmp/airbyte_local/destination.duckdb`.

## Access Replicated Data Files

If your Airbyte instance is running on the same computer that you are navigating with, you can open your browser and enter [file:///tmp/airbyte_local](file:///tmp/airbyte_local) to look at the replicated data locally. If the first approach fails or if your Airbyte instance is running on a remote server, follow the following steps to access the replicated files:

1. Access the scheduler container using `docker exec -it airbyte-server bash`
2. Navigate to the default local mount using `cd /tmp/airbyte_local`
3. Navigate to the replicated file directory you specified when you created the destination, using `cd /{destination_path}`
4. Execute `duckdb {filename}` to access the data in a particular database file.

You can also copy the output file to your host machine, the following command will copy the file to the current working directory you are using:

```text
docker cp airbyte-server:/tmp/airbyte_local/{destination_path} .
```

Note: If you are running Airbyte on Windows with Docker backed by WSL2, you have to use similar step as above or refer to this [link](/integrations/locating-files-local-destination.md) for an alternative approach.

<!-- /env:oss -->

## Troubleshooting

### Error message `Request failed:  (UNAVAILABLE, RPC 'GET_WELCOME_PACK')`

This error may indicate that you are connecting with a `0.10.x` DuckDB client (as per DuckDB Destination connector versions `>=0.4.0`) and your database has not yet been upgraded to a version `>=0.10.x`. To resolve this, you'll need to manually upgrade your database or revert to a previous version of the DuckDB Destination connector.
For information about migrating between different versions of DuckDB, please see the [DuckDB Migration Guide](./duckdb-migrations.md).



## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                                                                                                                                                                                                                                                                                                                                                                |
|:--------| :--------- | :-------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.5.1 | 2025-03-07 | [55256](https://github.com/airbytehq/airbyte/pull/55256) | Version bump to align Docker and Poetry versions |
| 0.5.0 | 2025-03-07 | [47861](https://github.com/airbytehq/airbyte/pull/47861) | Upgrade DuckDB engine version to [`v1.2.1`](https://github.com/duckdb/duckdb/releases/tag/v1.2.1) |
| 0.4.26 | 2024-10-29 | [47861](https://github.com/airbytehq/airbyte/pull/47861) | Update dependencies |
| 0.4.25 | 2024-10-28 | [47070](https://github.com/airbytehq/airbyte/pull/47070) | Update dependencies |
| 0.4.24 | 2024-10-12 | [46845](https://github.com/airbytehq/airbyte/pull/46845) | Update dependencies |
| 0.4.23 | 2024-10-05 | [46463](https://github.com/airbytehq/airbyte/pull/46463) | Update dependencies |
| 0.4.22 | 2024-09-28 | [46145](https://github.com/airbytehq/airbyte/pull/46145) | Update dependencies |
| 0.4.21 | 2024-09-21 | [45800](https://github.com/airbytehq/airbyte/pull/45800) | Update dependencies |
| 0.4.20 | 2024-09-14 | [45480](https://github.com/airbytehq/airbyte/pull/45480) | Update dependencies |
| 0.4.19 | 2024-09-07 | [45288](https://github.com/airbytehq/airbyte/pull/45288) | Update dependencies |
| 0.4.18 | 2024-08-31 | [44952](https://github.com/airbytehq/airbyte/pull/44952) | Update dependencies |
| 0.4.17 | 2024-08-24 | [44739](https://github.com/airbytehq/airbyte/pull/44739) | Update dependencies |
| 0.4.16 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.4.15 | 2024-08-17 | [44215](https://github.com/airbytehq/airbyte/pull/44215) | Update dependencies |
| 0.4.14 | 2024-08-12 | [43755](https://github.com/airbytehq/airbyte/pull/43755) | Update dependencies |
| 0.4.13 | 2024-08-10 | [43536](https://github.com/airbytehq/airbyte/pull/43536) | Update dependencies |
| 0.4.12 | 2024-08-03 | [43151](https://github.com/airbytehq/airbyte/pull/43151) | Update dependencies |
| 0.4.11 | 2024-07-27 | [42753](https://github.com/airbytehq/airbyte/pull/42753) | Update dependencies |
| 0.4.10 | 2024-07-20 | [42233](https://github.com/airbytehq/airbyte/pull/42233) | Update dependencies |
| 0.4.9 | 2024-07-13 | [41882](https://github.com/airbytehq/airbyte/pull/41882) | Update dependencies |
| 0.4.8 | 2024-07-10 | [41521](https://github.com/airbytehq/airbyte/pull/41521) | Update dependencies |
| 0.4.7 | 2024-07-09 | [41253](https://github.com/airbytehq/airbyte/pull/41253) | Update dependencies |
| 0.4.6 | 2024-07-06 | [41014](https://github.com/airbytehq/airbyte/pull/41014) | Update dependencies |
| 0.4.5 | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.4.4 | 2024-06-25 | [40354](https://github.com/airbytehq/airbyte/pull/40354) | Update dependencies |
| 0.4.3 | 2024-06-23 | [40224](https://github.com/airbytehq/airbyte/pull/40224) | Update dependencies |
| 0.4.2 | 2024-06-21 | [39947](https://github.com/airbytehq/airbyte/pull/39947) | Update dependencies |
| 0.4.1 | 2024-06-04 | [38959](https://github.com/airbytehq/airbyte/pull/38959) | [autopull] Upgrade base image to v1.2.1 |
| 0.4.0   | 2024-05-30 | [#37515](https://github.com/airbytehq/airbyte/pull/37515) | Upgrade DuckDB engine version to [`v0.10.3`](https://github.com/duckdb/duckdb/releases/tag/v0.10.2).                                                                                                                                                                                                                                                                                                                                              |
| 0.3.6   | 2024-05-21 | [#38486](https://github.com/airbytehq/airbyte/pull/38486)  | [autopull] base image + poetry + up_to_date                                                                                                                                                                                                                                                                                                                                                            |
| 0.3.5   | 2024-04-23 | [#37515](https://github.com/airbytehq/airbyte/pull/37515) | Add resource requirements declaration to `metatadat.yml`.                                                                                                                                                                                                                                                                                                                                              |
| 0.3.4   | 2024-04-16 | [#36715](https://github.com/airbytehq/airbyte/pull/36715) | Improve ingestion performance using pyarrow inmem view for writing to DuckDB.                                                                                                                                                                                                                                                                                                                          |
| 0.3.3   | 2024-04-07 | [#36884](https://github.com/airbytehq/airbyte/pull/36884) | Fix stale dependency versions in lock file, add CLI for internal testing.                                                                                                                                                                                                                                                                                                                              |
| 0.3.2   | 2024-03-20 | [#32635](https://github.com/airbytehq/airbyte/pull/32635) | Instrument custom_user_agent to identify Airbyte-Motherduck connector usage.                                                                                                                                                                                                                                                                                                                           |
| 0.3.1   | 2023-11-18 | [#32635](https://github.com/airbytehq/airbyte/pull/32635) | Upgrade DuckDB version to [`v0.9.2`](https://github.com/duckdb/duckdb/releases/tag/v0.9.2).                                                                                                                                                                                                                                                                                                            |
| 0.3.0   | 2022-10-23 | [#31744](https://github.com/airbytehq/airbyte/pull/31744) | Upgrade DuckDB version to [`v0.9.1`](https://github.com/duckdb/duckdb/releases/tag/v0.9.1). **Required update for all MotherDuck users.** Note, this is a **BREAKING CHANGE** for users who may have other connections using versions of DuckDB prior to 0.9.x. See the [0.9.0 release notes](https://github.com/duckdb/duckdb/releases/tag/v0.9.0) for more information and for upgrade instructions. |
| 0.2.1   | 2022-10-20 | [#30600](https://github.com/airbytehq/airbyte/pull/30600) | Fix: schema name mapping                                                                                                                                                                                                                                                                                                                                                                               |
| 0.2.0   | 2022-10-19 | [#29428](https://github.com/airbytehq/airbyte/pull/29428) | Add support for MotherDuck. Upgrade DuckDB version to `v0.8``.                                                                                                                                                                                                                                                                                                                                         |
| 0.1.0   | 2022-10-14 | [17494](https://github.com/airbytehq/airbyte/pull/17494)  | New DuckDB destination                                                                                                                                                                                                                                                                                                                                                                                 |

</details>
