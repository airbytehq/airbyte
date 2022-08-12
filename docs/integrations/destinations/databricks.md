# Databricks Lakehouse

## Overview

This destination syncs data to Delta Lake on Databricks Lakehouse. Each stream is written to its own [delta-table](https://delta.io/).

This connector requires a JDBC driver to connect to the Databricks cluster. By using the driver and the connector, you must agree to the [JDBC ODBC driver license](https://databricks.com/jdbc-odbc-driver-license). This means that you can only use this connector to connect third party applications to Apache Spark SQL within a Databricks offering using the ODBC and/or JDBC protocols.

Currently, this connector requires 30+MB of memory for each stream. When syncing multiple streams, it may run into an out-of-memory error if the allocated memory is too small. This performance bottleneck is tracked in [this issue](https://github.com/airbytehq/airbyte/issues/11424). Once this issue is resolved, the connector should be able to sync an almost infinite number of streams with less than 500MB of memory.

## Sync Mode

| Feature | Support | Notes |
| :--- | :---: | :--- |
| Full Refresh Sync | ✅ | Warning: this mode deletes all previously synced data in the configured bucket path. |
| Incremental - Append Sync | ✅ |  |
| Incremental - Deduped History | ❌ |  |
| Namespaces | ✅ |  |

## Data Source

Databricks Delta Lake supports various cloud storage as the [data source](https://docs.databricks.com/data/data-sources/index.html). Currently, only Amazon S3 is supported by this connector.

## Configuration

| Category         | Parameter             |  Type   | Notes                                                                                                                                                                                                                                                                                                                                                       |
|:-----------------|:----------------------|:-------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Databricks       | Server Hostname       | string  | Required. Example: `abc-12345678-wxyz.cloud.databricks.com`. See [documentation](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#get-server-hostname-port-http-path-and-jdbc-url). Please note that this is the server for the Databricks Cluster. It is different from the SQL Endpoint Cluster.                                             |
|                  | HTTP Path             | string  | Required. Example: `sql/protocolvx/o/1234567489/0000-1111111-abcd90`. See [documentation](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#get-server-hostname-port-http-path-and-jdbc-url).                                                                                                                                                   |
|                  | Port                  | string  | Optional. Default to "443". See [documentation](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#get-server-hostname-port-http-path-and-jdbc-url).                                                                                                                                                                                             |
|                  | Personal Access Token | string  | Required. Example: `dapi0123456789abcdefghij0123456789AB`. See [documentation](https://docs.databricks.com/sql/user/security/personal-access-tokens.html).                                                                                                                                                                                                  |
| General          | Database schema       | string  | Optional. Default to "public". Each data stream will be written to a table under this database schema.                                                                                                                                                                                                                                                      |
|                  | Purge Staging Data    | boolean | The connector creates staging files and tables on S3. By default, they will be purged when the data sync is complete. Set it to `false` for debugging purposes.                                                                                                                                                                                             |
| Data Source - S3 | Bucket Name           | string  | Name of the bucket to sync data into.                                                                                                                                                                                                                                                                                                                       |
|                  | Bucket Path           | string  | Subdirectory under the above bucket to sync the data into.                                                                                                                                                                                                                                                                                                  |
|                  | Region                | string  | See [documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions) for all region codes.                                                                                                                                                                                             |
|                  | Access Key ID         | string  | AWS/Minio credential.                                                                                                                                                                                                                                                                                                                                       |
|                  | Secret Access Key     | string  | AWS/Minio credential.                                                                                                                                                                                                                                                                                                                                       |
|                  | S3 Filename pattern   | string  | The pattern allows you to set the file-name format for the S3 staging file(s), next placeholders combinations are currently supported: {date}, {date:yyyy_MM}, {timestamp}, {timestamp:millis}, {timestamp:micros}, {part_number}, {sync_id}, {format_extension}. Please, don't use empty space and not supportable placeholders, as they won't recognized. |

⚠️ Please note that under "Full Refresh Sync" mode, data in the configured bucket and path will be wiped out before each sync. We recommend you provision a dedicated S3 resource for this sync to prevent unexpected data deletion from misconfiguration. ⚠️

## Staging Parquet Files (Delta Format)

Data streams are first written as staging delta-table ([Parquet](https://parquet.apache.org/) + [Transaction Log](https://databricks.com/blog/2019/08/21/diving-into-delta-lake-unpacking-the-transaction-log.html)) files on S3, and then loaded into Databricks delta-tables. All the staging files will be deleted after the sync is done. For debugging purposes, here is the full path for a staging file:

```text
s3://<bucket-name>/<bucket-path>/<uuid>/<stream-name>
```

For example:

```text
s3://testing_bucket/data_output_path/98c450be-5b1c-422d-b8b5-6ca9903727d9/users/_delta_log
     ↑              ↑                ↑                                    ↑     ↑
     |              |                |                                    |     transaction log
     |              |                |                                    stream name
     |              |                database schema
     |              bucket path
     bucket name
```

## Unmanaged Spark SQL Table

Currently, all streams are synced into unmanaged Spark SQL tables. See [documentation](https://docs.databricks.com/data/tables.html#managed-and-unmanaged-tables) for details. In summary, you have full control of the location of the data underlying an unmanaged table. The full path of each data stream is:

```text
s3://<bucket-name>/<bucket-path>/<database-schema>/<stream-name>
```

For example:

```text
s3://testing_bucket/data_output_path/public/users
     ↑              ↑                ↑      ↑
     |              |                |      stream name
     |              |                database schema
     |              bucket path
     bucket name
```

Please keep these data directories on S3. Otherwise, the corresponding tables will have no data in Databricks.

## Output Schema

Each table will have the following columns:

| Column | Type | Notes |
| :--- | :---: | :--- |
| `_airbyte_ab_id` | string | UUID. |
| `_airbyte_emitted_at` | timestamp | Data emission timestamp. |
| Data fields from the source stream | various | All fields in the staging Parquet files will be expanded in the table. |

Under the hood, an Airbyte data stream in Json schema is first converted to an Avro schema, then the Json object is converted to an Avro record, and finally the Avro record is outputted to the Parquet format. Because the data stream can come from any data source, the Json to Avro conversion process has arbitrary rules and limitations. Learn more about how source data is converted to Avro and the current limitations [here](https://docs.airbyte.io/understanding-airbyte/json-avro-conversion).

## Getting started

### Requirements

1. Credentials for a Databricks cluster. See [documentation](https://docs.databricks.com/clusters/create.html).
2. Credentials for an S3 bucket. See [documentation](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys).
3. Grant the Databricks cluster full access to the S3 bucket. Or mount it as Databricks File System \(DBFS\). See [documentation](https://docs.databricks.com/data/data-sources/aws/amazon-s3.html).

## CHANGELOG

| Version | Date       | Pull Request                                                                                                        | Subject                                                                                                               |
|:--------|:-----------|:--------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------|
| 0.2.6   | 2022-08-05 | [\#14801](https://github.com/airbytehq/airbyte/pull/14801)                                                          | Fix multiply log bindings                                                                                             |
| 0.2.5   | 2022-07-15 | [\#14494](https://github.com/airbytehq/airbyte/pull/14494)                                                          | Make S3 output filename configurable.                                                                                 |
| 0.2.4   | 2022-07-14 | [\#14618](https://github.com/airbytehq/airbyte/pull/14618)                                                          | Removed additionalProperties: false from JDBC destination connectors                                                  |
| 0.2.3   | 2022-06-16 | [\#13852](https://github.com/airbytehq/airbyte/pull/13852)                                                          | Updated stacktrace format for any trace message errors                                                                |
| 0.2.2   | 2022-06-13 | [\#13722](https://github.com/airbytehq/airbyte/pull/13722)                                                          | Rename to "Databricks Lakehouse".                                                                                     |
| 0.2.1   | 2022-06-08 | [\#13630](https://github.com/airbytehq/airbyte/pull/13630)                                                          | Rename to "Databricks Delta Lake" and add field orders in the spec.                                                   |
| 0.2.0   | 2022-05-15 | [\#12861](https://github.com/airbytehq/airbyte/pull/12861)                                                          | Use new public Databricks JDBC driver, and open source the connector.                                                 |
| 0.1.5   | 2022-05-04 | [\#12578](https://github.com/airbytehq/airbyte/pull/12578)                                                          | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                       |
| 0.1.4   | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256)                                                          | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                          |
| 0.1.3   | 2022-01-06 | [\#7622](https://github.com/airbytehq/airbyte/pull/7622) [\#9153](https://github.com/airbytehq/airbyte/issues/9153) | Upgrade Spark JDBC driver to `2.6.21` to patch Log4j vulnerability; update connector fields title/description.        |
| 0.1.2   | 2021-11-03 | [\#7288](https://github.com/airbytehq/airbyte/issues/7288)                                                          | Support Json `additionalProperties`.                                                                                  |
| 0.1.1   | 2021-10-05 | [\#6792](https://github.com/airbytehq/airbyte/pull/6792)                                                            | Require users to accept Databricks JDBC Driver [Terms & Conditions](https://databricks.com/jdbc-odbc-driver-license). |
| 0.1.0   | 2021-09-14 | [\#5998](https://github.com/airbytehq/airbyte/pull/5998)                                                            | Initial private release.                                                                                              |
