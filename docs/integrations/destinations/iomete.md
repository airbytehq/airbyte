# Iomete

## Overview

This page describes the step-by-step process of setting up the iomete destination connector.

Setting up the iomete destination connector involves setting up iomete components (lakehouse, database, schema, user, and role) in the iomete console.

## Prerequisites
- An iomete account. If you do not have an account yet, use self [sign-up](https://app.iomete.com/signup) or reach out via intercom chat and we'll help you on your way.
- A running lakehouse cluster.

## Supported Sync Mode

| Feature | Support | Notes |
| :--- | :---: | :--- |
| Full Refresh Sync | ✅ | Warning: this mode deletes all previously synced data in the configured bucket path. |
| Incremental - Append Sync | ✅ |  |

## Configuration

| Category     | Parameter                |  Type   | Notes                                                                                                                                                                                                                                                                                                                                                       |
|:-------------|:-------------------------|:-------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| iomete       | Lakehouse Connection URL | string  | Required. Example: `airbyte://frankfurt.iomete.com/12312421312/default`. This is a combination of hostname, account number and lakehouse name. See [documentation](https://iomete.com/docs/airbyte-connection) how to get Lakehouse connection url from iomete platform.                                                                                    |
|              | Username                 | string  | Required. Username to use to access iomete.                                                                                                                                                                                                                                                                                                                 |
|              | Password                 | string  | Required. Password associated with username.                                                                                                                                                                                                                                                                                                                |
| General      | Database schema          | string  | Optional. Default is "default". Each data stream will be written to a table under this database schema.                                                                                                                                                                                                                                                     |
| Staging - S3 | Bucket Name              | string  | Name of the bucket to sync data into.                                                                                                                                                                                                                                                                                                                       |
|              | Bucket Path              | string  | Subdirectory under the above bucket to sync the data into.                                                                                                                                                                                                                                                                                                  |
|              | Region                   | string  | See [documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html#concepts-available-regions) for all region codes.                                                                                                                                                                                             |
|              | Access Key ID            | string  | AWS/Minio credential.                                                                                                                                                                                                                                                                                                                                       |
|              | Secret Access Key        | string  | AWS/Minio credential.                                                                                                                                                                                                                                                                                                                                       |
|              | S3 Filename pattern      | string  | The pattern allows you to set the file-name format for the S3 staging file(s), next placeholders combinations are currently supported: {date}, {date:yyyy_MM}, {timestamp}, {timestamp:millis}, {timestamp:micros}, {part_number}, {sync_id}, {format_extension}. Please, don't use empty space and not supportable placeholders, as they won't recognized. |
|              | Purge Staging Data       | boolean | The connector creates staging files and tables on S3. By default, they will be purged when the data sync is complete. Set it to `false` for debugging purposes.                                                                                                                                                                                             |

⚠️ Please note that under "Full Refresh Sync" mode, data in the configured bucket and path will be wiped out before each sync. We recommend you provision a dedicated S3 resource for this sync to prevent unexpected data deletion from misconfiguration. ⚠️

## Staging
The storage that Airbyte uses as a staging area. Airbyte will read/write to this staging area. Lakehouse only needs a read access. Currently, only supports S3.

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

* See the [documentation](https://iomete.com/docs/how-to-sync-data-from-aws-s3-to-iomete) how to manage staging data access for iomete.

### iomete tutorials

* [How to get Lakehouse connection URL from iomete platform](https://iomete.com/docs/airbyte-connection)

## Changelog

| Version | Date       | Pull Request | Subject                 |
|:--------|:-----------| :-----       |:------------------------|
| 0.1.0  | 2022-09-29 | [17240](https://github.com/airbytehq/airbyte/pull/17240) | New Destination: iomete |