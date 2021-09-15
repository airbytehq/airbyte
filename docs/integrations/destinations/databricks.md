# Databricks

## Overview

This destination syncs data to Databricks cluster. Each stream is written to its own table.

This connector requires a JDBC driver to connect to Databricks cluster. The driver is developed by Simba. Before using the driver and the connector, you must agree to the [JDBC ODBC driver license](https://databricks.com/jdbc-odbc-driver-license). This means that you can only use this connector to connector third party applications to Apache Spark SQL within a Databricks offering using the ODBC and/or JDBC protocols.

Due to legal reasons, this is currently a private connector that is only available in Airbyte Cloud. We are working on publicizing it. Please follow [this issue](https://github.com/airbytehq/airbyte/issues/6043) for progress.

## Sync Mode

| Feature | Support | Notes |
| :--- | :---: | :--- |
| Full Refresh Sync | ✅ | Warning: this mode deletes all previously synced data in the configured bucket path. |
| Incremental - Append Sync | ✅ | |
| Incremental - Dedupe Sync | ❌ | |
| Namespaces | ✅ | |

## Data Source
Databricks supports various cloud storage as the [data source](https://docs.databricks.com/data/data-sources/index.html). Currently, only Amazon S3 is supported.

## Configuration

| Category | Parameter | Type | Notes |
| :--- | :--- | :---: | :--- |
| Databricks | Server Hostname | string | Required. See [documentation](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#get-server-hostname-port-http-path-and-jdbc-url). |
| | HTTP Path | string | Required. See [documentation](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#get-server-hostname-port-http-path-and-jdbc-url). |
| | Port | string | Optional. Default to "443". See [documentation](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#get-server-hostname-port-http-path-and-jdbc-url). |
| | Personal Access Token | string | Required. See [documentation](https://docs.databricks.com/sql/user/security/personal-access-tokens.html). |
| General | Database schema | string | Optional. Default to "public". Each data stream will be written to a table under this database schema. |
| | Purge Staging Data | boolean | The connector creates staging files and tables on S3. By default they will be purged when the data sync is complete. Set it to `false` for debugging purpose. |
| Data Source - S3 | Bucket Name | string | Name of the bucket to sync data into. |
| | Bucket Path | string | Subdirectory under the above bucket to sync the data into. |
| | Region | string | See [documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions) for all region codes. |
| | Access Key ID | string | AWS/Minio credential. |
| | Secret Access Key | string | AWS/Minio credential. |

⚠️ Please note that under "Full Refresh Sync" mode, data in the configured bucket and path will be wiped out before each sync. We recommend you to provision a dedicated S3 resource for this sync to prevent unexpected data deletion from misconfiguration. ⚠️

## Staging Parquet Files

Data streams are first written as staging Parquet files on S3, and then loaded into Databricks tables. All the staging files will be deleted after the sync is done. For debugging purposes, here is the full path for a staging file:

```
s3://<bucket-name>/<bucket-path>/<uuid>/<stream-name>
```

For example:

```
s3://testing_bucket/data_output_path/98c450be-5b1c-422d-b8b5-6ca9903727d9/users
     ↑              ↑                ↑                                    ↑
     |              |                |                                    stream name
     |              |                database schema
     |              bucket path
     bucket name
```


## Unmanaged Spark SQL Table

Currently, all streams are synced into unmanaged Spark SQL tables. See [documentation](https://docs.databricks.com/data/tables.html#managed-and-unmanaged-tables) for details. In summary, you have full control of the location of the data underlying an unmanaged table. The full path of each data stream is:

```
s3://<bucket-name>/<bucket-path>/<database-schema>/<stream-name>
```

For example:

```
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

Learn how source data is converted to Parquet and the current limitations [here](https://docs.airbyte.io/integrations/destinations/s3#data-schema).

## Getting started

### Requirements

1. Credentials for a Databricks cluster. See [documentation](https://docs.databricks.com/clusters/create.html).
2. Credentials for an S3 bucket. See [documentation](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys).
3. Grant the Databricks cluster full access to the S3 bucket. Or mount it as Databricks File System (DBFS). See [documentation](https://docs.databricks.com/data/data-sources/aws/amazon-s3.html).

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- |
| 0.1.0 | 2021-09-14 | [#5998](https://github.com/airbytehq/airbyte/pull/5998) | Initial private release. |
