---
description: >-
  BigQuery is a serverless, highly scalable, and cost-effective data warehouse
  offered by Google Cloud Provider.
---

# BigQuery

## Overview

The Airbyte BigQuery destination allows you to sync data to BigQuery.

This BigQuery destination is based on the [PipelineWise BigQuery Target](https://github.com/transferwise/pipelinewise-target-bigquery).

### Sync overview

#### Output schema

Airbyte Streams and Fields are written as BigQuery Tables and Columns respectively, applying the type changes described below. No extra columns are added in the process.

#### Data type mapping

| Airbyte Type | BigQuery Type | Notes |
| :--- | :--- | :--- |
| `array` | `array` or `string` | arrays are converted into BigQuery arrays using the type mappings defined here. If the array's item type is not supported by Airbyte, the whole array is encoded as a string. |
| `boolean` | `boolean` |  |
| `date-time` | `timestamp` |  |
| `integer` | `integer` |  |
| `number` | `numeric` |  |
| `object` | `struct`/`record` | fields of the written struct are converted according to the conversions in this table |
| `string` | `string` |  |
| Types not listed above | `string` |  |

#### Features

This section should contain a table with the following format:

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |

## Getting started

### Requirements

To use the BigQuery destination, you'll need:

* A Google Cloud Project with BigQuery enabled
* A BigQuery Dataset into which Airbyte can sync your data
* A Google Cloud Service Account with the "BigQuery User" role
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

Note that queries written in BigQueries can only reference Datasets in the same physical location. So if you plan on combining the data Airbyte synced with data from other datasets in your queries, make sure you create the datasets in the same location on Google Cloud. See the [Introduction to Datasets](https://cloud.google.com/bigquery/docs/datasets-intro) section for more info on considerations around creating Datasets.

#### Service account

In order for Airbyte to sync data into BigQuery, it needs credentials for a [Service Account](https://cloud.google.com/iam/docs/service-accounts) with the "BigQuery User" role, which grants permissions to run BigQuery jobs, write to BigQuery Datasets, and read table metadata.We highly recommend that this Service Account is exclusive to Airbyte for ease of permissioning and auditing. However, you can use a pre-existing Service Account if you already have one with the correct permissions.

The easiest way to create a Service Account is to follow GCP's guide for [Creating a Service Account](https://cloud.google.com/iam/docs/creating-managing-service-accounts). Once you've created the Service Account, make sure to keep its ID handy as you will need to reference it when granting roles. Service Account IDs typically take the form `<account-name>@<project-name>.iam.gserviceaccount.com`

Then, add the service account as a Member in your Google Cloud Project with the "BigQuery User" role. To do this, follow the instructions for [Granting Access](https://cloud.google.com/iam/docs/granting-changing-revoking-access#granting-console) in the Google documentation. The email address of the member you are adding is the same as the Service Account ID you just created.

At this point you should have a service account with the "BigQuery User" project-level permission.

#### Service account key

Service Account Keys are used to authenticate as Google Service Accounts. For Airbyte to leverage the permissions you granted to the Service Account in the previous step, you'll need to provide its Service Account Keys. See the [Google documentation](https://cloud.google.com/iam/docs/service-accounts#service_account_keys) for more information about Keys.

Follow the [Creating and Managing Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys) guide to create a key. Airbyte currently supports JSON Keys only, so make sure you create your key in that format. As soon as you created the key, make sure to download it, as that is the only time Google will allow you to see its contents. Once you've successfully configured BigQuery as a destination in Airbyte, delete this key from your computer.

### Setup the BigQuery destination in Airbyte

You should now have all the requirements needed to configure BigQuery as a destination in the UI. You'll need the following information to configure the BigQuery destination:

* **Project ID**
* **Dataset ID**
* **Service Account Key**: the contents of your Service Account Key JSON file
* **Default Target Schema:** the name of the schema where the tables will be created. In most cases, this should match the Dataset ID. 

Once you've configured BigQuery as a destination, delete the Service Account Key from your computer.

