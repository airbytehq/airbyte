# MeiliSearch

## Overview

The Airbyte MeilSearch destination allows you to sync data to MeiliSearch. MeiliSearch is a search
engine that makes it easy for a non-developer to search through data. It does not require any SQL.

### Sync overview

#### Output schema

Each stream will be output into its own index in MeiliSearch. Each table will be named after the
stream with all non-alpha numeric characters removed. Each table will contain one column per
top-levelfield in a stream. In addition, it will contain a table called `_ab_pk`. This column is
used internally by Airbyte to prevent records from getting overwritten and can be ignored.

#### Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | No                   |       |
| Namespaces                     | No                   |       |

## Getting started

### Requirements

To use the MeiliSearch destination, you'll need an existing MeiliSearch instance. You can learn
about how to create one in the
[MeiliSearch docs](https://www.meilisearch.com/docs/learn/getting_started/installation).

### Setup guide

The setup only requires two fields. First is the `host` which is the address at which MeiliSearch
can be reached. If running on a localhost by default it will be on `http://localhost:7700`. Note
that you must include the protocol. The second piece of information is the API key. If no API key is
set for your MeiliSearch instance, then this field can be left blank. If it is set, you can find the
value for your API by following these
[instructions](https://docs.meilisearch.com/reference/features/authentication.html#master-key). in
the MeiliSearch docs.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                |
| :------ | :--------- | :-------------------------------------------------------- | :----------------------------------------------------- |
| 1.0.16 | 2025-02-22 | [54221](https://github.com/airbytehq/airbyte/pull/54221) | Update dependencies |
| 1.0.15 | 2025-02-15 | [53896](https://github.com/airbytehq/airbyte/pull/53896) | Update dependencies |
| 1.0.14 | 2025-02-01 | [52876](https://github.com/airbytehq/airbyte/pull/52876) | Update dependencies |
| 1.0.13 | 2025-01-25 | [52206](https://github.com/airbytehq/airbyte/pull/52206) | Update dependencies |
| 1.0.12 | 2025-01-11 | [51270](https://github.com/airbytehq/airbyte/pull/51270) | Update dependencies |
| 1.0.11 | 2025-01-04 | [50909](https://github.com/airbytehq/airbyte/pull/50909) | Update dependencies |
| 1.0.10 | 2024-12-28 | [50460](https://github.com/airbytehq/airbyte/pull/50460) | Update dependencies |
| 1.0.9 | 2024-12-21 | [50196](https://github.com/airbytehq/airbyte/pull/50196) | Update dependencies |
| 1.0.8 | 2024-12-14 | [49550](https://github.com/airbytehq/airbyte/pull/49550) | Update dependencies |
| 1.0.7 | 2024-12-11 | [49021](https://github.com/airbytehq/airbyte/pull/49021) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.0.6 | 2024-11-04 | [48207](https://github.com/airbytehq/airbyte/pull/48207) | Update dependencies |
| 1.0.5 | 2024-10-29 | [47889](https://github.com/airbytehq/airbyte/pull/47889) | Update dependencies |
| 1.0.4 | 2024-10-28 | [47646](https://github.com/airbytehq/airbyte/pull/47646) | Update dependencies |
| 1.0.3   | 2024-07-08 | [#TODO](https://github.com/airbytehq/airbyte/pull/TODO) | Switching to Poetry and base image                                   |
| 1.0.2   | 2024-03-05 | [#35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector                                   |
| 1.0.1   | 2023-12-19 | [27692](https://github.com/airbytehq/airbyte/pull/27692)  | Fix incomplete data indexing                           |
| 1.0.0   | 2022-10-26 | [18036](https://github.com/airbytehq/airbyte/pull/18036)  | Migrate MeiliSearch to Python CDK                      |
| 0.2.13  | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864)  | Updated stacktrace format for any trace message errors |
| 0.2.12  | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)  | Add `-XX:+ExitOnOutOfMemoryError` JVM option           |
| 0.2.11  | 2021-12-28 | [9156](https://github.com/airbytehq/airbyte/pull/9156)    | Update connector fields title/description              |

</details>
