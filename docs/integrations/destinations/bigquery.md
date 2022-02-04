---
description: >-
  BigQuery is a serverless, highly scalable, and cost-effective data warehouse
  offered by Google Cloud Provider.
---

# BigQuery

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Deduped History | Yes |  |
| Bulk loading | Yes |  |
| Namespaces | Yes |  |

There are two flavors of connectors for this destination:

1. Bigquery: This is producing the standard Airbyte outputs using a `_airbyte_raw_*` tables storing the JSON blob data first. Afterward, these are transformed and normalized into separate tables, potentially "exploding" nested streams into their own tables if [basic normalization](../../understanding-airbyte/basic-normalization.md) is configured. 
2. `Bigquery (Denormalized)`: Instead of splitting the final data into multiple tables, this destination leverages BigQuery capabilities with [Structured and Repeated fields](https://cloud.google.com/bigquery/docs/nested-repeated) to produce a single "big" table per stream. This does not write the `_airbyte_raw_*` tables in the destination and normalization from this connector is not supported at this time.

## Troubleshooting

Check out common troubleshooting issues for the BigQuery destination connector on our Discourse [here](https://discuss.airbyte.io/tags/c/connector/11/destination-bigquery).

## Output Schema for BigQuery

Each stream will be output into its own table in BigQuery. Each table will contain 3 columns:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in BigQuery is `String`.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source. The column type in BigQuery is `Timestamp`.
* `_airbyte_data`: a json blob representing with the event data. The column type in BigQuery is `String`.

The output tables from the BigQuery destination are partitioned and clustered by the Time-unit column `_airbyte_emitted_at` at a daily granularity. Partitions boundaries are based on UTC time.
This is useful to limit the number of partitions scanned when querying these partitioned tables, by using a predicate filter (a WHERE clause). Filters on the partitioning column will be used to prune the partitions and reduce the query cost. (The parameter "Require partition filter" is not enabled by Airbyte, but you may toggle this by updating the produced tables if you wish so)

## Getting Started \(Airbyte Open-Source / Airbyte Cloud\)

#### Requirements

To use the BigQuery destination, you'll need:

* A Google Cloud Project with BigQuery enabled
* A BigQuery Dataset into which Airbyte can sync your data
* A Google Cloud Service Account with the "BigQuery User" and "BigQuery Data Editor" roles in your GCP project
* A Service Account Key to authenticate into your Service Account

For GCS Staging upload mode:

* GCS role enabled for same user as used for biqquery
* HMAC key obtained for user. Currently, only the [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) is supported. More credential types will be added in the future.

See the setup guide for more information about how to create the required resources.

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

You should now have all the requirements needed to configure BigQuery as a destination in the UI. You'll need the following information to configure the BigQuery destination:

* **Project ID**
* **Dataset Location**
* **Dataset ID**: the name of the schema where the tables will be created.
* **Service Account Key**: the contents of your Service Account Key JSON file

Additional options can also be customized:

* **Google BigQuery client chunk size**: Google BigQuery client's chunk\(buffer\) size \(MIN=1, MAX = 15\) for each table. The default 15MiB value is used if not set explicitly. It's recommended to decrease value for big data sets migration for less HEAP memory consumption and avoiding crashes. For more details refer to [https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html](https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html)
* **Transformation Priority**: configure the priority of queries run for transformations. Refer to [https://cloud.google.com/bigquery/docs/running-queries](https://cloud.google.com/bigquery/docs/running-queries). By default, Airbyte runs interactive query jobs on BigQuery, which means that the query is executed as soon as possible and count towards daily concurrent quotas and limits. If set to use batch query on your behalf, BigQuery starts the query as soon as idle resources are available in the BigQuery shared resource pool. This usually occurs within a few minutes. If BigQuery hasn't started the query within 24 hours, BigQuery changes the job priority to interactive. Batch queries don't count towards your concurrent rate limit, which can make it easier to start many queries at once.

Once you've configured BigQuery as a destination, delete the Service Account Key from your computer.

## Uploading Options

There are 2 available options to upload data to BigQuery `Standard` and `GCS Staging`.

### `GCS Staging` 

This is the recommended configuration for uploading data to BigQuery. It works by first uploading all the data to a [GCS](https://cloud.google.com/storage) bucket, then ingesting the data to BigQuery. To configure GCS Staging, you'll need the following parameters:
* **GCS Bucket Name**
* **GCS Bucket Path**
* **Block Size (MB) for GCS multipart upload**
* **GCS Bucket Keep files after migration**
  * See [this](https://cloud.google.com/storage/docs/creating-buckets) for instructions on how to create a GCS bucket. The bucket cannot have a retention policy. Set Protection Tools to none or Object versioning.
* **HMAC Key Access ID**
  * See [this](https://cloud.google.com/storage/docs/authentication/managing-hmackeys) on how to generate an access key. For more information on hmac keys please reference the [GCP docs](https://cloud.google.com/storage/docs/authentication/hmackeys)
  * We recommend creating an Airbyte-specific user or service account. This user or account will require the following permissions for the bucket:
    ```
    storage.multipartUploads.abort
    storage.multipartUploads.create
    storage.objects.create
    storage.objects.delete
    storage.objects.get
    storage.objects.list
    ```
    You can set those by going to the permissions tab in the GCS bucket and adding the appropriate the email address of the service account or user and adding the aforementioned permissions.
* **Secret Access Key**
  * Corresponding key to the above access ID.
* Make sure your GCS bucket is accessible from the machine running Airbyte. This depends on your networking setup. The easiest way to verify if Airbyte is able to connect to your GCS bucket is via the check connection tool in the UI.

### `Standard` uploads 
This uploads data directly from your source to BigQuery. While this is faster to setup initially, **we strongly recommend that you do not use this option for anything other than a quick demo**. It is more than 10x slower than the GCS uploading option and will fail for many datasets. Please be aware you may see some failures for big datasets and slow sources, e.g. if reading from source takes more than 10-12 hours. This is caused by the Google BigQuery SDK client limitations. For more details please check [https://github.com/airbytehq/airbyte/issues/3549](https://github.com/airbytehq/airbyte/issues/3549)

## Naming Conventions

From [BigQuery Datasets Naming](https://cloud.google.com/bigquery/docs/datasets#dataset-naming):

When you create a dataset in BigQuery, the dataset name must be unique for each project. The dataset name can contain the following:

* Up to 1,024 characters.
* Letters \(uppercase or lowercase\), numbers, and underscores.

  Note: In the Cloud Console, datasets that begin with an underscore are hidden from the navigation pane. You can query tables and views in these datasets even though these datasets aren't visible.

* Dataset names are case-sensitive: mydataset and MyDataset can coexist in the same project.
* Dataset names cannot contain spaces or special characters such as -, &, @, or %.

Therefore, Airbyte BigQuery destination will convert any invalid characters into '\_' characters when writing data.

## CHANGELOG

### bigquery

| Version | Date | Pull Request | Subject |
|:--------| :--- | :--- | :--- |
| 0.6.6   | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959) | Fix null pointer exception from buffered stream consumer. |
| 0.6.6   | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745) | Integrate with Sentry. |
| 0.6.5   | 2022-01-18 | [\#9573](https://github.com/airbytehq/airbyte/pull/9573)   | BigQuery Destination : update description for some input fields |
| 0.6.4   | 2022-01-17 | [\#8383](https://github.com/airbytehq/airbyte/issues/8383) | Support dataset-id prefixed by project-id |
| 0.6.3   | 2022-01-12 | [\#9415](https://github.com/airbytehq/airbyte/pull/9415)   | BigQuery Destination : Fix GCS processing of Facebook data |
| 0.6.2   | 2022-01-10 | [\#9121](https://github.com/airbytehq/airbyte/pull/9121)   | Fixed check method for GCS mode to verify if all roles assigned to user |
| 0.6.1   | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration to UI for GCS staging |
| 0.6.0   | 2021-12-17 | [\#8788](https://github.com/airbytehq/airbyte/issues/8788) | BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files |
| 0.5.1   | 2021-12-16 | [\#8816](https://github.com/airbytehq/airbyte/issues/8816) | Update dataset locations |
| 0.5.0   | 2021-10-26 | [\#7240](https://github.com/airbytehq/airbyte/issues/7240) | Output partitioned/clustered tables |
| 0.4.1   | 2021-10-04 | [\#6733](https://github.com/airbytehq/airbyte/issues/6733) | Support dataset starting with numbers |
| 0.4.0   | 2021-08-26 | [\#5296](https://github.com/airbytehq/airbyte/issues/5296) | Added GCS Staging uploading option |
| 0.3.12  | 2021-08-03 | [\#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add optional arg to make a possibility to change the BigQuery client's chunk\buffer size |
| 0.3.11  | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125) | Enable `additionalPropertities` in spec.json |
| 0.3.10  | 2021-07-28 | [\#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add extended logs and made JobId filled with region and projectId |
| 0.3.9   | 2021-07-28 | [\#5026](https://github.com/airbytehq/airbyte/pull/5026) | Add sanitized json fields in raw tables to handle quotes in column names |
| 0.3.6   | 2021-06-18 | [\#3947](https://github.com/airbytehq/airbyte/issues/3947) | Service account credentials are now optional. |
| 0.3.4   | 2021-06-07 | [\#3277](https://github.com/airbytehq/airbyte/issues/3277) | Add dataset location option |

### bigquery-denormalized

| Version | Date       | Pull Request                                               | Subject |
|:--------|:-----------|:-----------------------------------------------------------| :--- |
| 0.2.7   | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959) | Fix null pointer exception from buffered stream consumer. |
| 0.2.6   | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745) | Integrate with Sentry. |
| 0.2.5   | 2022-01-18 | [\#9573](https://github.com/airbytehq/airbyte/pull/9573)   | BigQuery Destination : update description for some input fields |
| 0.2.4   | 2022-01-17 | [\#8383](https://github.com/airbytehq/airbyte/issues/8383) | BigQuery/BiqQuery denorm Destinations : Support dataset-id prefixed by project-id |
| 0.2.3   | 2022-01-12 | [\#9415](https://github.com/airbytehq/airbyte/pull/9415)   | BigQuery Destination : Fix GCS processing of Facebook data |
| 0.2.2   | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration to UI for GCS staging |
| 0.2.1   | 2021-12-21 | [\#8574](https://github.com/airbytehq/airbyte/pull/8574)   | Added namespace to Avro and Parquet record types |
| 0.2.0   | 2021-12-17 | [\#8788](https://github.com/airbytehq/airbyte/pull/8788)   |  BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files |
| 0.1.11  | 2021-12-16 | [\#8816](https://github.com/airbytehq/airbyte/issues/8816) | Update dataset locations |
| 0.1.10  | 2021-11-09 | [\#7804](https://github.com/airbytehq/airbyte/pull/7804)   |  handle null values in fields described by a $ref definition |
| 0.1.9   | 2021-11-08 | [\#7736](https://github.com/airbytehq/airbyte/issues/7736) | Fixed the handling of ObjectNodes with $ref definition key |
| 0.1.8   | 2021-10-27 | [\#7413](https://github.com/airbytehq/airbyte/issues/7413) | Fixed DATETIME conversion for BigQuery |
| 0.1.7   | 2021-10-26 | [\#7240](https://github.com/airbytehq/airbyte/issues/7240) | Output partitioned/clustered tables |
| 0.1.6   | 2021-09-16 | [\#6145](https://github.com/airbytehq/airbyte/pull/6145)   | BigQuery Denormalized support for date, datetime & timestamp types through the json "format" key |
| 0.1.5   | 2021-09-07 | [\#5881](https://github.com/airbytehq/airbyte/pull/5881)   | BigQuery Denormalized NPE fix |
| 0.1.4   | 2021-09-04 | [\#5813](https://github.com/airbytehq/airbyte/pull/5813)   | fix Stackoverflow error when receive a schema from source where "Array" type doesn't contain a required "items" element |
| 0.1.3   | 2021-08-07 | [\#5261](https://github.com/airbytehq/airbyte/pull/5261)   | 🐛 Destination BigQuery\(Denormalized\): Fix processing arrays of records |
| 0.1.2   | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json |
| 0.1.1   | 2021-06-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer |
| 0.1.0   | 2021-06-21 | [\#4176](https://github.com/airbytehq/airbyte/pull/4176)   | Destination using Typed Struct and Repeated fields |

