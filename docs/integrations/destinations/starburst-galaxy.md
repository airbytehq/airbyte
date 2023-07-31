# Starburst Galaxy destination user guide

## Overview

The Starburst Galaxy destination syncs data to Starburst Galaxy [great lake catalogs](https://docs.starburst.io/starburst-galaxy/sql/great-lakes.html)  
in [Apache Iceberg](https://iceberg.apache.org/) table format. Each stream is written to its own Iceberg table.

## Features

| Feature         | Supported | Notes                                                                               |
|:----------------|:---------:|:------------------------------------------------------------------------------------|
| Overwrite Sync  |     ✅     | **Warning**: this mode deletes all previously synced data in the destination table. |
| Append Sync     |     ✅     |                                                                                     |
| Deduped History |     ❌     |                                                                                     |
| Namespaces      |     ✅     |                                                                                     |
| SSL             |     ✅     | SSL is enabled.                                                                     |    

## Data storage

Starburst Galaxy supports various [object storages](https://docs.starburst.io/starburst-galaxy/catalogs/index.html#object-storage); 
however, only Amazon S3 is supported by this connector.

## Configuration

| Category                         | Parameter                     |  Type   | Notes                                                                                                                                                                                                                                                                                            |
|:---------------------------------|:------------------------------|:-------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Starburst Galaxy                 | `Hostname`                    | string  | Required. Located in the **Connection info** section of the [view clusters](https://docs.starburst.io/starburst-galaxy/clusters/index.html#manage-clusters) pane in Starburst Galaxy.                                                                                                            |
|                                  | `Port`                        | string  | Optional. Located in the **Connection info** section of the [view clusters](https://docs.starburst.io/starburst-galaxy/clusters/index.html#manage-clusters) pane in Starburst Galaxy. Defaults to `443`.                                                                                         |
|                                  | `User`                        | string  | Required. Galaxy user found in the **Connection info** section of the [view clusters](https://docs.starburst.io/starburst-galaxy/clusters/index.html#manage-clusters) pane in Starburst Galaxy.                                                                                                  |
|                                  | `Password`                    | string  | Required. Password for the specified Galaxy user.                                                                                                                                                                                                                                                |
|                                  | `Amazon S3 catalog`           | string  | Required. Name of the [Amazon S3 catalog](https://docs.starburst.io/starburst-galaxy/catalogs/s3.html) created in the Galaxy domain.                                                                                                                                                             |
|                                  | `Amazon S3 catalog schema`    | string  | Optional. The default Starburst Galaxy Amazon S3 catalog schema where tables are written to if the source does not specify a namespace. Each data stream is written to a table in this schema. Defaults to `public`.                                                                             |
| Staging Object Store - Amazon S3 | `Bucket name`                 | string  | Required. Name of the bucket where the staging data is stored.                                                                                                                                                                                                                                   |
|                                  | `Bucket path`                 | string  | Required. Sets the subdirectory of the specified S3 bucket used for storing staging data.                                                                                                                                                                                                        |
|                                  | `Bucket region`               | string  | Required. Sets the region of the specified S3 bucket.                                                                                                                                                                                                                                            |
|                                  | `Access key`                  | string  | Required. AWS/Minio credential.                                                                                                                                                                                                                                                                  |
|                                  | `Secret key`                  | string  | Required. AWS/Minio credential.                                                                                                                                                                                                                                                                  |
| General                          | `Purge staging Iceberg table` | boolean | Optional. Indicates that staging Iceberg table is purged after a data sync is complete. Enabled by default. Disable it for debugging purposes only.                                                                                                                                              |

## Staging files

### S3

Data streams are written to a temporary Iceberg table, and then loaded into Amazon S3 Starburst Galaxy catalog in the Iceberg table format. 
Staging table is deleted after a sync is complete if the `Purge staging Iceberg table` is enabled. 
The following is an example of a full path for a staging file:

```text
s3://<bucket-name>/<bucket-path>/<namespace/schema>/<temp Iceberg table name {_airbyte_tmp_random-three-chars_stream-name}>
```

For example:

```text
s3://galaxy_bucket/data_output_path/test_schema/_airbyte_tmp_qey_user
     ↑              ↑                     ↑                ↑
     |              |                     |                temporary Iceberg table holding data 
     |              |                     source namespace or provided schema name
     |              |                
     |              bucket path
     bucket name
```

## Target Iceberg SQL table

Streams are synced in the Starburst Galaxy Amazon S3 catalog with Iceberg table format.

## Output schema

Each table in the output schema has the following columns:

| Column                                                        |         Type          | Description                                                                                          |
|:--------------------------------------------------------------|:---------------------:|:-----------------------------------------------------------------------------------------------------|
| `_airbyte_ab_id`                                              |        varchar        | UUID.                                                                                                |
| `_airbyte_emitted_at`                                         |     timestamp(6)      | Data emission timestamp.                                                                             |
| Data fields from the source stream                            |        various        | All the fields from the source stream will be populated as an individual column in the target table. |
| `_airbyte_additional_properties`                              | map(varchar, varchar) | Additional properties.                                                                               |

The Airbyte data stream's JSON schema is converted to an Avro schema. The JSON object is then converted to an Avro record; 
the Avro record is written to a staging Iceberg table. As the data stream can be generated from any data source, 
the JSON-to-Avro conversion process has arbitrary rules and limitations. 
Learn more about [how source data is converted to Avro](https://docs.airbyte.io/understanding-airbyte/json-avro-conversion).

### Datatype support

Learn more about [Starburst Galaxy Iceberg type mapping](https://docs.starburst.io/latest/connector/iceberg.html#iceberg-to-trino-type-mapping). 

## Getting started

### Requirements

- [Starburst Galaxy cluster](https://docs.starburst.io/starburst-galaxy/clusters/index.html). Required credentials are found in the **Connection info** section of the [view clusters](https://docs.starburst.io/starburst-galaxy/clusters/index.html#manage-clusters) page
- A [Starburst Galaxy S3 catalog](https://docs.starburst.io/starburst-galaxy/catalogs/s3.html) created within the Galaxy domain, and [attached to a running cluster](https://docs.starburst.io/starburst-galaxy/catalogs/index.html#add-a-catalog-to-a-cluster).
- [Credentials for S3 bucket](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys).
- Grant S3 bucket [location privileges](https://docs.starburst.io/starburst-galaxy/security/privileges.html#location-privileges-) to the role user is assigned to.

## Changelog

| Version | Date       | Pull Request                                               | Subject                 |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------|
| 0.0.1   | 2023-03-28 | [\#24620](https://github.com/airbytehq/airbyte/pull/24620) | Initial public release. |
