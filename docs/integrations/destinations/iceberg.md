# Iceberg

This page guides you through the process of setting up the Iceberg destination connector.

## Sync overview

### Output schema

The incoming airbyte data is structured in keyspaces and tables and is partitioned and replicated across different nodes
in the cluster. This connector maps an incoming `stream` to an Iceberg `table` and a `namespace` to an
Iceberg `database`. Fields in the airbyte message become different columns in the Iceberg tables. Each table will
contain the following columns.

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

Every ten thousand pieces of incoming airbyte data in a stream ————we call it a batch, would produce one data file(
Parquet/Avro) in an Iceberg table. This batch size can be configurabled by `Data file flushing batch size`
property.
As the quantity of Iceberg data files grows, it causes an unnecessary amount of metadata and less efficient queries from
file open costs.
Iceberg provides data file compaction action to improve this case, you can read more about
compaction [HERE](https://iceberg.apache.org/docs/latest/maintenance/#compact-data-files).
This connector also provides auto compact action when stream closes, by `Auto compact data files` property. Any you can
specify the target size of compacted Iceberg data file.

## Getting started

### Requirements

- **Iceberg catalog** : Iceberg uses `catalog` to manage tables. this connector already supports:
  - [HiveCatalog](https://iceberg.apache.org/docs/latest/hive/#global-hive-catalog) connects to a **Hive metastore**
    to keep track of Iceberg tables.
  - [HadoopCatalog](https://iceberg.apache.org/docs/latest/java-api-quickstart/#using-a-hadoop-catalog) doesn’t need
    to connect to a Hive MetaStore, but can only be used with **HDFS or similar file systems** that support atomic
    rename. For `HadoopCatalog`, this connector use **Storage Config** (S3 or HDFS) to manage Iceberg tables.
  - [JdbcCatalog](https://iceberg.apache.org/docs/latest/jdbc/) uses a table in a relational database to manage
    Iceberg tables through JDBC. So far, this connector supports **PostgreSQL** only.
- **Storage medium** means where Iceberg data files storages in. So far, this connector supports **S3/S3N/S3N**
  object-storage only.

## Changelog

| Version | Date       | Pull Request                                             | Subject        |
| :------ | :--------- | :------------------------------------------------------- | :------------- |
| 0.1.0   | 2022-11-01 | [18836](https://github.com/airbytehq/airbyte/pull/18836) | Initial Commit |
