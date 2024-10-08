# Iceberg

<!-- env:cloud -->

:::caution

Cloud version is still in development iterations. DO NOT use for production purposes.

:::

<!-- /env:cloud -->

This page guides you through the process of setting up the Iceberg destination connector.

## Sync overview

### Output schema

The incoming airbyte data is structured in keyspaces and tables and is partitioned and replicated
across different nodes in the cluster. This connector maps an incoming `stream` to an Iceberg
`table` and a `namespace` to an Iceberg `database`. Fields in the airbyte message become different
columns in the Iceberg tables. Each table will contain the following columns.

- `_airbyte_ab_id`: A random generated uuid.
- `_airbyte_emitted_at`: a timestamp representing when the event was received from the data source.
- `_airbyte_data`: a json text representing the extracted data.

### Features

This section should contain a table with the following format:

| Feature                       | Supported?(Yes/No) | Notes |
| :---------------------------- | :----------------- | :---- |
| Full Refresh Sync             | ✅                 |       |
| Incremental Sync              | ✅                 |       |
| Replicate Incremental Deletes | ❌                 |       |
| SSH Tunnel Support            | ❌                 |       |

### Performance considerations

Every ten thousand pieces of incoming airbyte data in a stream ————we call it a batch, would produce
one data file( Parquet/Avro) in an Iceberg table. This batch size can be configurabled by
`Data file flushing batch size` property. As the quantity of Iceberg data files grows, it causes an
unnecessary amount of metadata and less efficient queries from file open costs. Iceberg provides
data file compaction action to improve this case, you can read more about compaction
[HERE](https://iceberg.apache.org/docs/latest/maintenance/#compact-data-files). This connector also
provides auto compact action when stream closes, by `Auto compact data files` property. Any you can
specify the target size of compacted Iceberg data file.

## Getting started

### Requirements

- **Iceberg catalog** : Iceberg uses `catalog` to manage tables. this connector already supports:
  - [HiveCatalog](https://iceberg.apache.org/docs/latest/hive/#global-hive-catalog) connects to a
    **Hive metastore** to keep track of Iceberg tables.
  - [HadoopCatalog](https://iceberg.apache.org/docs/latest/java-api-quickstart/#using-a-hadoop-catalog)
    doesn’t need to connect to a Hive MetaStore, but can only be used with **HDFS or similar file
    systems** that support atomic rename. For `HadoopCatalog`, this connector use **Storage Config**
    (S3 or HDFS) to manage Iceberg tables.
  - [JdbcCatalog](https://iceberg.apache.org/docs/latest/jdbc/) uses a table in a relational
    database to manage Iceberg tables through JDBC. So far, this connector supports **PostgreSQL**
    only.
  - [RESTCatalog](https://iceberg.apache.org/docs/latest/spark-configuration/#catalog-configuration)
    connects to a REST server, which manages Iceberg tables.
  - [GlueCatalog](https://iceberg.apache.org/docs/1.5.1/aws/#glue-catalog)
- **Storage medium** means where Iceberg data files storages in. So far, this connector supports
  **S3/S3N/S3N** object-storage. When using the RESTCatalog, it is possible to have storage be
  managed by the server.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                                        |
|:--------|:-----------|:----------------------------------------------------------|:---------------------------------------------------------------|
| 0.2.2   | 2024-09-23 | [45861](https://github.com/airbytehq/airbyte/pull/45861)  | Keeping only S3 with Glue Catalog as config option             |
| 0.2.1   | 2024-09-20 | [45711](https://github.com/airbytehq/airbyte/pull/45711)  | Initial Cloud version for registry purpose [UNTESTED ON CLOUD] |
| 0.2.0   | 2024-09-20 | [45707](https://github.com/airbytehq/airbyte/pull/45707)  | Add support for AWS Glue Catalog                               |
| 0.1.8   | 2024-09-16 | [45206](https://github.com/airbytehq/airbyte/pull/45206)  | Fixing tests to work in airbyte-ci                             |
| 0.1.7   | 2024-05-17 | [38283](https://github.com/airbytehq/airbyte/pull/38283)  | Bump Iceberg library to 1.5.2 and Spark to 3.5.1               |
| 0.1.6   | 2024-04-04 | [#36846](https://github.com/airbytehq/airbyte/pull/36846) | Remove duplicate S3 Region                                     |
| 0.1.5   | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924) | Add new ap-southeast-3 AWS region                              |
| 0.1.4   | 2023-07-20 | [28506](https://github.com/airbytehq/airbyte/pull/28506)  | Support server-managed storage config                          |
| 0.1.3   | 2023-07-12 | [28158](https://github.com/airbytehq/airbyte/pull/28158)  | Bump Iceberg library to 1.3.0 and add REST catalog support     |
| 0.1.2   | 2023-07-14 | [28345](https://github.com/airbytehq/airbyte/pull/28345)  | Trigger rebuild of image                                       |
| 0.1.1   | 2023-02-27 | [23201](https://github.com/airbytehq/airbyte/pull/23301)  | Bump Iceberg library to 1.1.0                                  |
| 0.1.0   | 2022-11-01 | [18836](https://github.com/airbytehq/airbyte/pull/18836)  | Initial Commit                                                 |

</details>