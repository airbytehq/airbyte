---
description: >-
  BigQuery is a serverless, highly scalable, and cost-effective data warehouse
  offered by Google Cloud Provider.
---

# BigQuery

## Overview

The BigQuery source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is running.

### Resulting schema

The BigQuery source does not alter the schema present in your database. Depending on the destination connected to this source, however, the schema may be altered. See the destination's documentation for more details.

### Data type mapping

The BigQuery data types mapping:

| BigQuery Type | Resulting Type | Notes             |
| :------------ | :------------- | :---------------- |
| `BOOL`        | Boolean        |                   |
| `INT64`       | Number         |                   |
| `FLOAT64`     | Number         |                   |
| `NUMERIC`     | Number         |                   |
| `BIGNUMERIC`  | Number         |                   |
| `STRING`      | String         |                   |
| `BYTES`       | String         |                   |
| `DATE`        | String         | In ISO8601 format |
| `DATETIME`    | String         | In ISO8601 format |
| `TIMESTAMP`   | String         | In ISO8601 format |
| `TIME`        | String         |                   |
| `ARRAY`       | Array          |                   |
| `STRUCT`      | Object         |                   |
| `GEOGRAPHY`   | String         |                   |

### Features

| Feature             | Supported | Notes |
| :------------------ | :-------- | :---- |
| Full Refresh Sync   | Yes       |       |
| Incremental Sync    | Yes       |       |
| Change Data Capture | No        |       |
| SSL Support         | Yes       |       |

## Getting started

### Requirements

To use the BigQuery source, you'll need:

- A Google Cloud Project with BigQuery enabled
- A Google Cloud Service Account with the "BigQuery User" and "BigQuery Data Editor" roles in your GCP project
- A Service Account Key to authenticate into your Service Account

See the setup guide for more information about how to create the required resources.

#### Service account

In order for Airbyte to sync data from BigQuery, it needs credentials for a [Service Account](https://cloud.google.com/iam/docs/service-accounts) with the "BigQuery User" and "BigQuery Data Editor" roles, which grants permissions to run BigQuery jobs, write to BigQuery Datasets, and read table metadata. We highly recommend that this Service Account is exclusive to Airbyte for ease of permissioning and auditing. However, you can use a pre-existing Service Account if you already have one with the correct permissions.

The easiest way to create a Service Account is to follow GCP's guide for [Creating a Service Account](https://cloud.google.com/iam/docs/creating-managing-service-accounts). Once you've created the Service Account, make sure to keep its ID handy as you will need to reference it when granting roles. Service Account IDs typically take the form `<account-name>@<project-name>.iam.gserviceaccount.com`

Then, add the service account as a Member in your Google Cloud Project with the "BigQuery User" role. To do this, follow the instructions for [Granting Access](https://cloud.google.com/iam/docs/granting-changing-revoking-access#granting-console) in the Google documentation. The email address of the member you are adding is the same as the Service Account ID you just created.

At this point you should have a service account with the "BigQuery User" project-level permission.

#### Service account key

Service Account Keys are used to authenticate as Google Service Accounts. For Airbyte to leverage the permissions you granted to the Service Account in the previous step, you'll need to provide its Service Account Keys. See the [Google documentation](https://cloud.google.com/iam/docs/service-accounts#service_account_keys) for more information about Keys.

Follow the [Creating and Managing Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) guide to create a key. Airbyte currently supports JSON Keys only, so make sure you create your key in that format. As soon as you created the key, make sure to download it, as that is the only time Google will allow you to see its contents. Once you've successfully configured BigQuery as a source in Airbyte, delete this key from your computer.

### Setup the BigQuery source in Airbyte

You should now have all the requirements needed to configure BigQuery as a source in the UI. You'll need the following information to configure the BigQuery source:

- **Project ID**
- **Default Dataset ID \[Optional\]**: the schema name if only one schema is interested. Dramatically boost source discover operation.
- **Credentials JSON**: the contents of your Service Account Key JSON file

Once you've configured BigQuery as a source, delete the Service Account Key from your computer.

## CHANGELOG

### source-bigquery

| Version | Date       | Pull Request                                             | Subject                                                                                                                                   |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| 0.4.2   | 2024-02-22 | [35503](https://github.com/airbytehq/airbyte/pull/35503) | Source BigQuery: replicating RECORD REPEATED fields                                                                                       |
| 0.4.1   | 2024-01-24 | [34453](https://github.com/airbytehq/airbyte/pull/34453) | bump CDK version                                                                                                                          |
| 0.4.0   | 2023-12-18 | [33484](https://github.com/airbytehq/airbyte/pull/33484) | Remove LEGACY state                                                                                                                       |
| 0.3.0   | 2023-06-26 | [27737](https://github.com/airbytehq/airbyte/pull/27737) | License Update: Elv2                                                                                                                      |
| 0.2.3   | 2022-10-13 | [15535](https://github.com/airbytehq/airbyte/pull/16238) | Update incremental query to avoid data missing when new data is inserted at the same time as a sync starts under non-CDC incremental mode |
| 0.2.2   | 2022-09-22 | [16902](https://github.com/airbytehq/airbyte/pull/16902) | Source BigQuery: added user agent header                                                                                                  |
| 0.2.1   | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668) | Wrap logs in AirbyteLogMessage                                                                                                            |
| 0.2.0   | 2022-07-26 | [14362](https://github.com/airbytehq/airbyte/pull/14362) | Integral columns are now discovered as int64 fields.                                                                                      |
| 0.1.9   | 2022-07-14 | [14574](https://github.com/airbytehq/airbyte/pull/14574) | Removed additionalProperties:false from JDBC source connectors                                                                            |
| 0.1.8   | 2022-06-17 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | Updated stacktrace format for any trace message errors                                                                                    |
| 0.1.7   | 2022-04-11 | [11484](https://github.com/airbytehq/airbyte/pull/11484) | BigQuery connector escape column names                                                                                                    |
| 0.1.6   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                              |
| 0.1.5   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications                                                                                         |
| 0.1.4   | 2021-09-30 | [\#6524](https://github.com/airbytehq/airbyte/pull/6524) | Allow `dataset_id` null in spec                                                                                                           |
| 0.1.3   | 2021-09-16 | [\#6051](https://github.com/airbytehq/airbyte/pull/6051) | Handle NPE `dataset_id` is not provided                                                                                                   |
| 0.1.2   | 2021-09-16 | [\#6135](https://github.com/airbytehq/airbyte/pull/6135) | 🐛 BigQuery source: Fix nested structs                                                                                                    |
| 0.1.1   | 2021-07-28 | [\#4981](https://github.com/airbytehq/airbyte/pull/4981) | 🐛 BigQuery source: Fix nested arrays                                                                                                     |
| 0.1.0   | 2021-07-22 | [\#4457](https://github.com/airbytehq/airbyte/pull/4457) | 🎉 New Source: Big Query.                                                                                                                 |
