---
description: >-
  BigQuery is a serverless, highly scalable, and cost-effective data warehouse
  offered by Google Cloud Provider.
---

# BigQuery

## Overview

The Airbyte BigQuery destination allows you to sync data to BigQuery. BigQuery is a serverless, highly scalable, and cost-effective data warehouse offered by Google Cloud Provider.

There are two flavors of connectors for this destination:
1. `destination-bigquery`: This is producing the standard Airbyte outputs using a `_airbyte_raw_*` tables storing the JSON blob data first. Afterward, these are transformed and normalized into separate tables, potentially "exploding" nested streams into their own tables if [basic normalization](../../understanding-airbyte/basic-normalization.md) is configured. 
2. `destination-bigquery-denormalized`: Instead of splitting the final data into multiple tables, this destination leverages BigQuery capabilities with [Structured and Repeated fields](https://cloud.google.com/bigquery/docs/nested-repeated) to produce a single "big" table per stream. This does not write the `_airbyte_raw_*` tables in the destination and normalization from this connector is not supported at this time.

### Sync overview

#### Output schema of `destination-bigquery`

Each stream will be output into its own table in BigQuery. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in BigQuery is `String`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in BigQuery is `Timestamp`.
* `_airbyte_data`: a json blob representing with the event data. The column type in BigQuery is `String`.

#### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Namespaces | Yes |  |

## Getting started

### Requirements

To use the BigQuery destination, you'll need:

* A Google Cloud Project with BigQuery enabled
* A BigQuery Dataset into which Airbyte can sync your data
* A Google Cloud Service Account with the "BigQuery User" and "BigQuery Data Editor" roles in your GCP project
* A Service Account Key to authenticate into your Service Account

See the setup guide for more information about how to create the required resources.

### Setup guide

#### Google cloud project

If you have a Google Cloud Project with BigQuery enabled, skip to the "Create a Dataset" section.

First, follow along the Google Cloud instructions to [Create a Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin).

**Enable BigQuery**

BigQuery is typically enabled automatically in new projects. If this is not the case for your project, follow the "Before you begin" section in the [BigQuery QuickStart](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui) docs.

#### BigQuery dataset for Airbyte syncs

Airbyte needs a location in BigQuery to write the data being synced from your data sources. If you already have a Dataset into which Airbyte should sync data, skip this section. Otherwise, follow the Google Cloud guide for [Creating a Dataset via the Console UI](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui#create_a_dataset) to achieve this.

Note that queries written in BigQuery can only reference Datasets in the same physical location. So if you plan on combining the data Airbyte synced with data from other datasets in your queries, make sure you create the datasets in the same location on Google Cloud. See the [Introduction to Datasets](https://cloud.google.com/bigquery/docs/datasets-intro) section for more info on considerations around creating Datasets.

#### Service account

In order for Airbyte to sync data into BigQuery, it needs credentials for a [Service Account](https://cloud.google.com/iam/docs/service-accounts) with the "BigQuery User" and "BigQuery Data Editor" roles, which grants permissions to run BigQuery jobs, write to BigQuery Datasets, and read table metadata. We highly recommend that this Service Account is exclusive to Airbyte for ease of permissioning and auditing. However, you can use a pre-existing Service Account if you already have one with the correct permissions.

The easiest way to create a Service Account is to follow GCP's guide for [Creating a Service Account](https://cloud.google.com/iam/docs/creating-managing-service-accounts). Once you've created the Service Account, make sure to keep its ID handy as you will need to reference it when granting roles. Service Account IDs typically take the form `<account-name>@<project-name>.iam.gserviceaccount.com`

Then, add the service account as a Member in your Google Cloud Project with the "BigQuery User" role. To do this, follow the instructions for [Granting Access](https://cloud.google.com/iam/docs/granting-changing-revoking-access#granting-console) in the Google documentation. The email address of the member you are adding is the same as the Service Account ID you just created.

At this point you should have a service account with the "BigQuery User" project-level permission.

#### Service account key

Service Account Keys are used to authenticate as Google Service Accounts. For Airbyte to leverage the permissions you granted to the Service Account in the previous step, you'll need to provide its Service Account Keys. See the [Google documentation](https://cloud.google.com/iam/docs/service-accounts#service_account_keys) for more information about Keys.

Follow the [Creating and Managing Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) guide to create a key. Airbyte currently supports JSON Keys only, so make sure you create your key in that format. As soon as you created the key, make sure to download it, as that is the only time Google will allow you to see its contents. Once you've successfully configured BigQuery as a destination in Airbyte, delete this key from your computer.

### Setup the BigQuery destination in Airbyte

You should now have all the requirements needed to configure BigQuery as a destination in the UI. You'll need the following information to configure the BigQuery destination:

* **Project ID**
* **Dataset Location**
* **Dataset ID**: the name of the schema where the tables will be created.
* **Service Account Key**: the contents of your Service Account Key JSON file
* **Google BigQuery client chunk size**: Google BigQuery client's chunk(buffer) size (MIN=1, MAX = 15) for each table. The default 15MiB value is used if not set explicitly. It's recommended to decrease value for big data sets migration for less HEAP memory consumption and avoiding crashes. For more details refer to https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html

Once you've configured BigQuery as a destination, delete the Service Account Key from your computer.

## Notes about BigQuery Naming Conventions

From [BigQuery Datasets Naming](https://cloud.google.com/bigquery/docs/datasets#dataset-naming):

When you create a dataset in BigQuery, the dataset name must be unique for each project. The dataset name can contain the following:

* Up to 1,024 characters.
* Letters \(uppercase or lowercase\), numbers, and underscores.

  Note: In the Cloud Console, datasets that begin with an underscore are hidden from the navigation pane. You can query tables and views in these datasets even though these datasets aren't visible.

* Dataset names are case-sensitive: mydataset and MyDataset can coexist in the same project.
* Dataset names cannot contain spaces or special characters such as -, &, @, or %.

Therefore, Airbyte BigQuery destination will convert any invalid characters into '\_' characters when writing data.

## CHANGELOG

### destination-bigquery

| Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- |
| 0.3.12 | 2021-08-03 | [#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add optional arg to make a possibility to change the BigQuery client's chunk\buffer size |
| 0.3.11 | 2021-07-30 | [#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.3.10 | 2021-07-28 | [#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add extended logs and made JobId filled with region and projectId |
| 0.3.9 | 2021-07-28 | [#5026](https://github.com/airbytehq/airbyte/pull/5026) | Add sanitized json fields in raw tables to handle quotes in column names |
| 0.3.6 | 2021-06-18 | [#3947](https://github.com/airbytehq/airbyte/issues/3947) | Service account credentials are now optional. |
| 0.3.4 | 2021-06-07 | [#3277](https://github.com/airbytehq/airbyte/issues/3277) | Add dataset location option |

### destination-bigquery-denormalized

| Version | Date | Pull Request | Subject |
| :--- | :---  | :--- | :--- |
| 0.1.4 | 2021-09-04 | [#5813](https://github.com/airbytehq/airbyte/pull/5813) | fix Stackoverflow error when receive a schema from source where "Array" type doesn't contain a required "items" element |
| 0.1.3 | 2021-08-07 | [#5261](https://github.com/airbytehq/airbyte/pull/5261) | 🐛 Destination BigQuery(Denormalized): Fix processing arrays of records |
| 0.1.2 | 2021-07-30 | [#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.1.1 | 2021-06-21 | [#3555](https://github.com/airbytehq/airbyte/pull/3555) | Partial Success in BufferedStreamConsumer |
| 0.1.0 | 2021-06-21 | [#4176](https://github.com/airbytehq/airbyte/pull/4176) | Destination using Typed Struct and Repeated fields |
