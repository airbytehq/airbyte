# BigQuery

This page guides you through the process of setting up the BigQuery destination connector.

## Prerequisites

* [A Google Cloud Project with BigQuery enabled](https://docs.airbyte.com/integrations/destinations/bigquery#google-cloud-project)
* [A BigQuery Dataset into which Airbyte can sync your data](https://docs.airbyte.com/integrations/destinations/bigquery#bigquery-dataset-for-airbyte-syncs)
* [A Google Cloud Service Account with the "BigQuery User" and "BigQuery Data Editor" roles in your GCP project](https://docs.airbyte.com/integrations/destinations/bigquery#service-account)
* [A Service Account Key to authenticate into your Service Account](https://docs.airbyte.com/integrations/destinations/bigquery#service-account-key)

## Setup guide

## Step 1: Set up BigQuery

To use the BigQuery destination, you'll need:

* [A Google Cloud Project with BigQuery enabled](https://docs.airbyte.com/integrations/destinations/bigquery#google-cloud-project)
* [A BigQuery Dataset into which Airbyte can sync your data](https://docs.airbyte.com/integrations/destinations/bigquery#bigquery-dataset-for-airbyte-syncs)
* [A Google Cloud Service Account with the "BigQuery User" and "BigQuery Data Editor" roles in your GCP project](https://docs.airbyte.com/integrations/destinations/bigquery#service-account)
* [A Service Account Key to authenticate into your Service Account](https://docs.airbyte.com/integrations/destinations/bigquery#service-account-key)

For GCS Staging upload mode:

* GCS role enabled for same user as used for biqquery
* HMAC key obtained for user. Currently, only
  the [HMAC key](https://cloud.google.com/storage/docs/authentication/hmackeys) is supported. More
  credential types will be added in the future.

See the setup guide for more information about how to create the required resources.

#### Google cloud project

If you have a Google Cloud Project with BigQuery enabled, skip to the "Create a Dataset" section.

First, follow along the Google Cloud instructions
to [Create a Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#before_you_begin)
.

**Enable BigQuery**

BigQuery is typically enabled automatically in new projects. If this is not the case for your
project, follow the "Before you begin" section in
the [BigQuery QuickStart](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui)
docs.

#### BigQuery dataset for Airbyte syncs

Airbyte needs a location in BigQuery to write the data being synced from your data sources. If you
already have a Dataset into which Airbyte should sync data, skip this section. Otherwise, follow the
Google Cloud guide
for [Creating a Dataset via the Console UI](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui#create_a_dataset)
to achieve this.

Note that queries written in BigQuery can only reference Datasets in the same physical location. So
if you plan on combining the data Airbyte synced with data from other datasets in your queries, make
sure you create the datasets in the same location on Google Cloud. See
the [Introduction to Datasets](https://cloud.google.com/bigquery/docs/datasets-intro) section for
more info on considerations around creating Datasets.

#### Service account

In order for Airbyte to sync data into BigQuery, it needs credentials for
a [Service Account](https://cloud.google.com/iam/docs/service-accounts) with
the `BigQuery User`(`roles/bigquery.user`) and `BigQuery Data Editor`(`roles/bigquery.dataEditor`)
roles, which grants permissions to run BigQuery jobs, write to BigQuery Datasets, and read table
metadata. More read about BigQuery roles permissions ypu can
read [here](https://cloud.google.com/bigquery/docs/access-control).

![create a service account with the bigquery user and data editor roles](https://user-images.githubusercontent.com/1933157/168459232-6b88458c-a038-4bc1-883d-cf506e363441.png)

We highly recommend that this Service Account is exclusive to Airbyte for ease of permissioning and
auditing. However, you can use a pre-existing Service Account if you already have one with the
correct permissions.

* `BigQuery User`(`roles/bigquery.user`) role permissions:

    ```
    bigquery.bireservations.get
    bigquery.capacityCommitments.get
    bigquery.capacityCommitments.list
    bigquery.config.get
    bigquery.datasets.create
    bigquery.datasets.get
    bigquery.datasets.getIamPolicy
    bigquery.jobs.create
    bigquery.jobs.list
    bigquery.models.list
    bigquery.readsessions.*
    bigquery.reservationAssignments.list
    bigquery.reservationAssignments.search
    bigquery.reservations.get
    bigquery.reservations.list
    bigquery.routines.list
    bigquery.savedqueries.get
    bigquery.savedqueries.list
    bigquery.tables.list
    bigquery.transfers.get
    resourcemanager.projects.get
    resourcemanager.projects.list
    ```
* `BigQuery Data Editor` (`roles/bigquery.dataEditor`) role permissions:
    ```
    bigquery.config.get
    bigquery.datasets.create
    bigquery.datasets.get
    bigquery.datasets.getIamPolicy
    bigquery.datasets.updateTag
    bigquery.models.*
    bigquery.routines.*
    bigquery.tables.create
    bigquery.tables.createSnapshot
    bigquery.tables.delete
    bigquery.tables.export
    bigquery.tables.get
    bigquery.tables.getData
    bigquery.tables.getIamPolicy
    bigquery.tables.list
    bigquery.tables.restoreSnapshot
    bigquery.tables.update
    bigquery.tables.updateData
    bigquery.tables.updateTag
    resourcemanager.projects.get
    resourcemanager.projects.list
    ```

#### Service account key json (required for cloud, optional for open source)

Service Account Keys are used to authenticate as Google Service Accounts. For Airbyte to leverage
the permissions you granted to the Service Account in the previous step, you'll need to provide its
Service Account Keys. See
the [Google documentation](https://cloud.google.com/iam/docs/service-accounts#service_account_keys)
for more information about Keys.

Follow
the [Creating and Managing Service Account Keys](https://cloud.google.com/iam/docs/creating-managing-service-account-keys)
guide to create a key. Airbyte currently supports JSON Keys only, so make sure you create your key
in that format. As soon as you created the key, make sure to download it, as that is the only time
Google will allow you to see its contents. Once you've successfully configured BigQuery as a
destination in Airbyte, delete this key from your computer.

The key JSON looks like the following (copied from the
example [here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating)):

```json
{
  "type": "service_account",
  "project_id": "<PROJECT_ID>",
  "private_key_id": "<KEY_ID>",
  "private_key": "-----BEGIN PRIVATE KEY-----\n<PRIVATE_KEY>\n-----END PRIVATE KEY-----\n",
  "client_email": "<SERVICE_ACCOUNT_EMAIL>",
  "client_id": "<CLIENT_ID>",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/<SERVICE_ACCOUNT_EMAIL>"
}
```

This parameter is **REQUIRED** when you set up the connector on cloud. It is only optional if you
deploy Airbyte in your own infra and provide the credential through the environment. The service
account key json will be searched in the following order:

- Credentials file pointed to by the `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Credentials provided by the Google Cloud SDK `gcloud auth application-default login` command
- Google App Engine built-in credentials
- Google Cloud Shell built-in credentials
- Google Compute Engine built-in credentials

See
the [Authenticating as a service account](https://cloud.google.com/docs/authentication/production#automatically)
for details.

----

You should now have all the requirements needed to configure BigQuery as a destination in the UI.
You'll need the following information to configure the BigQuery destination:

* **Project ID**
* **Dataset Location**
* **Dataset ID**: the name of the schema where the tables will be created.
* **Service Account Key**: the contents of your Service Account Key JSON file

Additional options can also be customized:

* **Google BigQuery client chunk size**: Google BigQuery client's chunk\(buffer\) size \(MIN=1, MAX
  = 15\) for each table. The default 15MiB value is used if not set explicitly. It's recommended to
  decrease value for big data sets migration for less HEAP memory consumption and avoiding crashes.
  For more details refer
  to [https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html](https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.client.Client.html)
* **Transformation Priority**: configure the priority of queries run for transformations. Refer
  to [https://cloud.google.com/bigquery/docs/running-queries](https://cloud.google.com/bigquery/docs/running-queries)
  . By default, Airbyte runs interactive query jobs on BigQuery, which means that the query is
  executed as soon as possible and count towards daily concurrent quotas and limits. If set to use
  batch query on your behalf, BigQuery starts the query as soon as idle resources are available in
  the BigQuery shared resource pool. This usually occurs within a few minutes. If BigQuery hasn't
  started the query within 24 hours, BigQuery changes the job priority to interactive. Batch queries
  don't count towards your concurrent rate limit, which can make it easier to start many queries at
  once.

Once you've configured BigQuery as a destination, delete the Service Account Key from your computer.

## Step 2: Set up the `BigQuery` connector in Airbyte

There are two flavors of connectors for this destination:

1. `Bigquery`: This is producing the standard Airbyte outputs using a `_airbyte_raw_*` tables
   storing the JSON blob data first. Afterward, these are transformed and normalized into separate
   tables, potentially "exploding" nested streams into their own tables
   if [basic normalization](../../understanding-airbyte/basic-normalization.md) is configured.
2. `Bigquery (Denormalized)`: Instead of splitting the final data into multiple tables, this
   destination leverages BigQuery capabilities
   with [Structured and Repeated fields](https://cloud.google.com/bigquery/docs/nested-repeated) to
   produce a single "big" table per stream. This does not write the `_airbyte_raw_*` tables in the
   destination and normalization from this connector is not supported at this time.

### Set up BigQuery For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **`Destinations`**. In the top-right corner, click **+new
   destination**.
3. On the Set up the destination page, enter the name for the BigQuery connector and select **BigQuery**
   from the Destination type dropdown.
4. Enter your `Dataset ID`, `Project ID`
5. Choose the `Loading method` type `Standart inserts` or `GCS Staging`
6. For `GCS Staging` choose `Credential` and type `GCS Bucket name`, `GCS Bucket path` and optional
   fields `Block Size` and choose `GCS Tmp Files Afterward Processing`
7. Enter `Service Account Key JSON`
8. Enter `Dataset Location`
9. Choose `Transformation Query Run Type` (by default it's interactive)
9. Type `Google BigQuery Client Chunk Size` (optional, by default it's 15)
10. Click on `Check Connection` to finish configuring the BigQuery destination.

### Set up BigQuery (denormalized) For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **`Destinations`**. In the top-right corner, click **+new
   destination**.
3. On the Set up the destination page, enter the name for the BigQuery connector and select **BigQuery (denormalized typed struct)**
   from the Destination type dropdown.
4. Enter your `Dataset ID`, `Project ID`
5. Choose the `Loading method` type `Standart inserts` or `GCS Staging`
6. For `GCS Staging` choose `Credential` and type `GCS Bucket name`, `GCS Bucket path` and optional
   fields `Block Size` and choose `GCS Tmp Files Afterward Processing`
7. Enter `Service Account Key JSON`
8. Choose `Dataset Location`
9. Type `Google BigQuery Client Chunk Size` (optional, by default it's 15)
10. Click on `Check Connection` to finish configuring the BigQuery destination.

### Set up BigQuery for Airbyte OSS:###
1. Go to local Airbyte UI.
2. In the left navigation bar, click **`Destinations`**. In the top-right corner, click **+new
   destination**.
3. On the Set up the destination page, enter the name for the BigQuery connector and select **BigQuery**
   from the Destination type dropdown.
4. Enter your `Dataset ID`, `Project ID`
5. Choose the `Loading method` type `Standart inserts` or `GCS Staging`
6. For `GCS Staging` choose `Credential` and type `GCS Bucket name`, `GCS Bucket path` and optional
   fields `Block Size` and choose `GCS Tmp Files Afterward Processing`
7. Enter `Service Account Key JSON`
8. Enter `Dataset Location`
9. Choose `Transformation Query Run Type` (by default it's interactive)
9. Type `Google BigQuery Client Chunk Size` (optional, by default it's 15)
10. Click on `Check Connection` to finish configuring the BigQuery destination.

### Set up BigQuery (denormalized) for Airbyte OSS:###

1. Go to local Airbyte UI.
2. In the left navigation bar, click **`Destinations`**. In the top-right corner, click **+new
   destination**.
3. On the Set up the destination page, enter the name for the BigQuery connector and select **BigQuery (denormalized typed struct)**
   from the Destination type dropdown.
4. Enter your `Dataset ID`, `Project ID`
5. Choose the `Loading method` type `Standart inserts` or `GCS Staging`
6. For `GCS Staging` choose `Credential` and type `GCS Bucket name`, `GCS Bucket path` and optional
   fields `Block Size` and choose `GCS Tmp Files Afterward Processing`
7. Enter `Service Account Key JSON` (Optional)
8. Choose `Dataset Location`
9. Type `Google BigQuery Client Chunk Size` (optional, by default it's 15)
10. Click on `Check Connection` to finish configuring the BigQuery destination.

## Supported sync modes

The BigQuery destination connector supports the
following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature | Supported? \(Yes/No\) | Notes |
| :--- |:----------------------| :--- |
| Full Refresh Sync | Yes                   |  |
| Incremental - Append Sync | Yes                   |  |
| Incremental - Deduped History | Yes                   |  |
| Bulk loading | Yes                   |  |
| Namespaces | Yes                   |  |

## Datatype mapping

| Airbyte type                        | BigQuery type | BigQuery denormalized type |
|:------------------------------------|:--------------|:---------------------------|
| DATE                                | DATE          | DATE                       |
| STRING (BASE64)                     | STRING        | STRING                     |
| NUMBER                              | FLOAT         | FLOAT                      |
| OBJECT                              | STRING        | RECORD                     |
| STRING                              | STRING        | STRING                     |
| BOOLEAN                             | BOOLEAN       | BOOLEAN                    |
| INTEGER                             | INTEGER       | INTEGER                    |
| STRING (BIG_NUMBER)                 | STRING        | STRING                     |
| STRING (BIG_INTEGER)                | STRING        | STRING                     |
| ARRAY                               | REPEATED      | REPEATED                   |
| STRING (TIMESTAMP_WITH_TIMEZONE)    | TIMESTAMP     | DATETIME                   |
| STRING (TIMESTAMP_WITHOUT_TIMEZONE) | TIMESTAMP     | DATETIME                   |

## Loading Method

There are 2 available options to upload data to BigQuery `Standard` and `GCS Staging`.

### `GCS Staging`

This is the recommended configuration for uploading data to BigQuery. It works by first uploading
all the data to a [GCS](https://cloud.google.com/storage) bucket, then ingesting the data to
BigQuery. To configure GCS Staging, you'll need the following parameters:

* **GCS Bucket Name**
* **GCS Bucket Path**
* **Block Size (MB) for GCS multipart upload**
* **GCS Bucket Keep files after migration**
    * See [this](https://cloud.google.com/storage/docs/creating-buckets) for instructions on how to
      create a GCS bucket. The bucket cannot have a retention policy. Set Protection Tools to none
      or Object versioning.
* **HMAC Key Access ID**
    * See [this](https://cloud.google.com/storage/docs/authentication/managing-hmackeys) on how to
      generate an access key. For more information on hmac keys please reference
      the [GCP docs](https://cloud.google.com/storage/docs/authentication/hmackeys).
      ![add hmac key to the bigquery service account](https://user-images.githubusercontent.com/1933157/168459101-f6d59db4-ebd6-4307-b528-f47b2ccf11e3.png)
    * The BigQuery service account (see the doc [above](#service-account)) should have the following
      permissions for the bucket:
      ```
      storage.multipartUploads.abort
      storage.multipartUploads.create
      storage.objects.create
      storage.objects.delete
      storage.objects.get
      storage.objects.list
      ```
    * The `Storage Object Admin` role has a superset of all the above permissions. So the quickest
      way is to add that role to the BigQuery service account in the IAM page as shown below.
      ![add storage object admin role to bigquery service account](https://user-images.githubusercontent.com/1933157/168458678-f3223a58-9403-4780-87dd-f44806f11d67.png)
    * Alternatively, create a dedicated role with just the above permissions, and assign this role
      to the BigQuery service account. In this way, the service account will have the minimum
      permissions required.
      ![create a dedicated role for gcs access](https://user-images.githubusercontent.com/1933157/168458835-05794756-4b2a-462f-baae-6811b61e9d22.png)

* **Secret Access Key**
    * Corresponding key to the above access ID.
* Make sure your GCS bucket is accessible from the machine running Airbyte. This depends on your
  networking setup. The easiest way to verify if Airbyte is able to connect to your GCS bucket is
  via the check connection tool in the UI.

### `Standard` uploads

This uploads data directly from your source to BigQuery. While this is faster to setup initially, **
we strongly recommend that you do not use this option for anything other than a quick demo**. It is
more than 10x slower than the GCS uploading option and will fail for many datasets. Please be aware
you may see some failures for big datasets and slow sources, e.g. if reading from source takes more
than 10-12 hours. This is caused by the Google BigQuery SDK client limitations. For more details
please
check [https://github.com/airbytehq/airbyte/issues/3549](https://github.com/airbytehq/airbyte/issues/3549)

## Notes about BigQuery Naming Conventions

From [BigQuery Datasets Naming](https://cloud.google.com/bigquery/docs/datasets#dataset-naming):

When you create a dataset in BigQuery, the dataset name must be unique for each project. The dataset
name can contain the following:

* Up to 1,024 characters.
* Letters \(uppercase or lowercase\), numbers, and underscores.

  Note: In the Cloud Console, datasets that begin with an underscore are hidden from the navigation
  pane. You can query tables and views in these datasets even though these datasets aren't visible.

* Dataset names are case-sensitive: mydataset and MyDataset can coexist in the same project.
* Dataset names cannot contain spaces or special characters such as -, &, @, or %.

Therefore, Airbyte BigQuery destination will convert any invalid characters into `_` characters when
writing data.

Since datasets that begin with `_` will be hidden from the BigQuery Explorer panel. To avoid
creating such datasets, the destination will prepend the namespace with `n` if the converted
namespace

## Common Root Causes of Permission Issues

The service account does not have the proper permissions.

- Make sure the BigQuery service account has `BigQuery User` and `BigQuery Data Editor` roles, or
  equivalent permissions as those two roles.
- If the GCS staging mode is selected, make sure the BigQuery service account has the right
  permissions to the GCS bucket and path, or the `Cloud Storage Admin` role, which includes a super
  set of the required permissions.

The HMAC key is wrong.

- Make sure the HMAC key is created for the BigQuery service account, and the service account has
  the permission to access the GCS bucket and path.

## CHANGELOG

### bigquery

| Version | Date       | Pull Request                                               | Subject                                                                                         |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------|
| 1.1.8   | 2022-06-07 | [13579](https://github.com/airbytehq/airbyte/pull/13579)   | Always check GCS bucket for GCS loading method to catch invalid HMAC keys. |
| 1.1.7   | 2022-06-07 | [13424](https://github.com/airbytehq/airbyte/pull/13424)   | Reordered fields for specification.                                                             |
| 1.1.6   | 2022-05-15 | [12768](https://github.com/airbytehq/airbyte/pull/12768)   | Clarify that the service account key json field is required on cloud. |
| 1.1.5   | 2022-05-12 | [12805](https://github.com/airbytehq/airbyte/pull/12805)   | Updated to latest base-java to emit AirbyteTraceMessage on error.                               |
| 1.1.4   | 2022-05-04 | [12578](https://github.com/airbytehq/airbyte/pull/12578)   | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging. |
| 1.1.3   | 2022-05-02 | [12528](https://github.com/airbytehq/airbyte/pull/12528)   | Update Dataset location field description                                                       |
| 1.1.2   | 2022-04-29 | [12477](https://github.com/airbytehq/airbyte/pull/12477)   | Dataset location is a required field                                                            |
| 1.1.1   | 2022-04-15 | [12068](https://github.com/airbytehq/airbyte/pull/12068)   | Fixed bug with GCS bucket conditional binding                                                   |
| 1.1.0   | 2022-04-06 | [11776](https://github.com/airbytehq/airbyte/pull/11776)   | Use serialized buffering strategy to reduce memory consumption.                                 |
| 1.0.2   | 2022-03-30 | [11620](https://github.com/airbytehq/airbyte/pull/11620)   | Updated spec                                                                                    |
| 1.0.1   | 2022-03-24 | [11350](https://github.com/airbytehq/airbyte/pull/11350)   | Improve check performance                                                                       |
| 1.0.0   | 2022-03-18 | [11238](https://github.com/airbytehq/airbyte/pull/11238)   | Updated spec and documentation                                                                  |
| 0.6.12  | 2022-03-18 | [10793](https://github.com/airbytehq/airbyte/pull/10793)   | Fix namespace with invalid characters                                                           |
| 0.6.11  | 2022-03-03 | [10755](https://github.com/airbytehq/airbyte/pull/10755)   | Make sure to kill children threads and stop JVM                                                 |
| 0.6.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                    |
| 0.6.6   | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959)   | Fix null pointer exception from buffered stream consumer.                                       |
| 0.6.6   | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745)   | Integrate with Sentry.                                                                          |
| 0.6.5   | 2022-01-18 | [\#9573](https://github.com/airbytehq/airbyte/pull/9573)   | BigQuery Destination : update description for some input fields                                 |
| 0.6.4   | 2022-01-17 | [\#8383](https://github.com/airbytehq/airbyte/issues/8383) | Support dataset-id prefixed by project-id                                                       |
| 0.6.3   | 2022-01-12 | [\#9415](https://github.com/airbytehq/airbyte/pull/9415)   | BigQuery Destination : Fix GCS processing of Facebook data                                      |
| 0.6.2   | 2022-01-10 | [\#9121](https://github.com/airbytehq/airbyte/pull/9121)   | Fixed check method for GCS mode to verify if all roles assigned to user                         |
| 0.6.1   | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration to UI for GCS staging                                             |
| 0.6.0   | 2021-12-17 | [\#8788](https://github.com/airbytehq/airbyte/issues/8788) | BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files     |
| 0.5.1   | 2021-12-16 | [\#8816](https://github.com/airbytehq/airbyte/issues/8816) | Update dataset locations                                                                        |
| 0.5.0   | 2021-10-26 | [\#7240](https://github.com/airbytehq/airbyte/issues/7240) | Output partitioned/clustered tables                                                             |
| 0.4.1   | 2021-10-04 | [\#6733](https://github.com/airbytehq/airbyte/issues/6733) | Support dataset starting with numbers                                                           |
| 0.4.0   | 2021-08-26 | [\#5296](https://github.com/airbytehq/airbyte/issues/5296) | Added GCS Staging uploading option                                                              |
| 0.3.12  | 2021-08-03 | [\#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add optional arg to make a possibility to change the BigQuery client's chunk\buffer size        |
| 0.3.11  | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                    |
| 0.3.10  | 2021-07-28 | [\#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add extended logs and made JobId filled with region and projectId                               |
| 0.3.9   | 2021-07-28 | [\#5026](https://github.com/airbytehq/airbyte/pull/5026)   | Add sanitized json fields in raw tables to handle quotes in column names                        |
| 0.3.6   | 2021-06-18 | [\#3947](https://github.com/airbytehq/airbyte/issues/3947) | Service account credentials are now optional.                                                   |
| 0.3.4   | 2021-06-07 | [\#3277](https://github.com/airbytehq/airbyte/issues/3277) | Add dataset location option                                                                     |

### bigquery-denormalized

| Version | Date       | Pull Request                                               | Subject                                                                                                                 |
|:--------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------|
| 1.1.8   | 2022-06-07 | [13579](https://github.com/airbytehq/airbyte/pull/13579)   | Always check GCS bucket for GCS loading method to catch invalid HMAC keys. |
| 1.1.7   | 2022-06-07 | [13424](https://github.com/airbytehq/airbyte/pull/13424)   | Reordered fields for specification.                                                                                     |
| 1.1.6   | 2022-05-15 | [12768](https://github.com/airbytehq/airbyte/pull/12768)   | Clarify that the service account key json field is required on cloud.                                                   |
| 0.3.5   | 2022-05-12 | [12805](https://github.com/airbytehq/airbyte/pull/12805)   | Updated to latest base-java to emit AirbyteTraceMessage on error.                                                       |
| 0.3.4   | 2022-05-04 | [12578](https://github.com/airbytehq/airbyte/pull/12578)   | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                         |
| 0.3.3   | 2022-05-02 | [12528](https://github.com/airbytehq/airbyte/pull/12528)   | Update Dataset location field description                                                                               |
| 0.3.2   | 2022-04-29 | [12477](https://github.com/airbytehq/airbyte/pull/12477)   | Dataset location is a required field                                                                                    |
| 0.3.1   | 2022-04-15 | [11978](https://github.com/airbytehq/airbyte/pull/11978)   | Fixed emittedAt timestamp.                                                                                              |
| 0.3.0   | 2022-04-06 | [11776](https://github.com/airbytehq/airbyte/pull/11776)   | Use serialized buffering strategy to reduce memory consumption.                                                         |
| 0.2.15  | 2022-04-05 | [11166](https://github.com/airbytehq/airbyte/pull/11166)   | Fixed handling of anyOf and allOf fields                                                                                |
| 0.2.14  | 2022-04-02 | [11620](https://github.com/airbytehq/airbyte/pull/11620)   | Updated spec                                                                                                            |
| 0.2.13  | 2022-04-01 | [11636](https://github.com/airbytehq/airbyte/pull/11636)   | Added new unit tests                                                                                                    |
| 0.2.12  | 2022-03-28 | [11454](https://github.com/airbytehq/airbyte/pull/11454)   | Integration test enhancement for picking test-data and schemas                                                          |
| 0.2.11  | 2022-03-18 | [10793](https://github.com/airbytehq/airbyte/pull/10793)   | Fix namespace with invalid characters                                                                                   |
| 0.2.10  | 2022-03-03 | [10755](https://github.com/airbytehq/airbyte/pull/10755)   | Make sure to kill children threads and stop JVM                                                                         |
| 0.2.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                            |
| 0.2.7   | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959)   | Fix null pointer exception from buffered stream consumer.                                                               |
| 0.2.6   | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745)   | Integrate with Sentry.                                                                                                  |
| 0.2.5   | 2022-01-18 | [\#9573](https://github.com/airbytehq/airbyte/pull/9573)   | BigQuery Destination : update description for some input fields                                                         |
| 0.2.4   | 2022-01-17 | [\#8383](https://github.com/airbytehq/airbyte/issues/8383) | BigQuery/BiqQuery denorm Destinations : Support dataset-id prefixed by project-id                                       |
| 0.2.3   | 2022-01-12 | [\#9415](https://github.com/airbytehq/airbyte/pull/9415)   | BigQuery Destination : Fix GCS processing of Facebook data                                                              |
| 0.2.2   | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration to UI for GCS staging                                                                     |
| 0.2.1   | 2021-12-21 | [\#8574](https://github.com/airbytehq/airbyte/pull/8574)   | Added namespace to Avro and Parquet record types                                                                        |
| 0.2.0   | 2021-12-17 | [\#8788](https://github.com/airbytehq/airbyte/pull/8788)   | BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files                             |
| 0.1.11  | 2021-12-16 | [\#8816](https://github.com/airbytehq/airbyte/issues/8816) | Update dataset locations                                                                                                |
| 0.1.10  | 2021-11-09 | [\#7804](https://github.com/airbytehq/airbyte/pull/7804)   | handle null values in fields described by a $ref definition                                                             |
| 0.1.9   | 2021-11-08 | [\#7736](https://github.com/airbytehq/airbyte/issues/7736) | Fixed the handling of ObjectNodes with $ref definition key                                                              |
| 0.1.8   | 2021-10-27 | [\#7413](https://github.com/airbytehq/airbyte/issues/7413) | Fixed DATETIME conversion for BigQuery                                                                                  |
| 0.1.7   | 2021-10-26 | [\#7240](https://github.com/airbytehq/airbyte/issues/7240) | Output partitioned/clustered tables                                                                                     |
| 0.1.6   | 2021-09-16 | [\#6145](https://github.com/airbytehq/airbyte/pull/6145)   | BigQuery Denormalized support for date, datetime & timestamp types through the json "format" key                        |
| 0.1.5   | 2021-09-07 | [\#5881](https://github.com/airbytehq/airbyte/pull/5881)   | BigQuery Denormalized NPE fix                                                                                           |
| 0.1.4   | 2021-09-04 | [\#5813](https://github.com/airbytehq/airbyte/pull/5813)   | fix Stackoverflow error when receive a schema from source where "Array" type doesn't contain a required "items" element |
| 0.1.3   | 2021-08-07 | [\#5261](https://github.com/airbytehq/airbyte/pull/5261)   | 🐛 Destination BigQuery\(Denormalized\): Fix processing arrays of records                                               |
| 0.1.2   | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                                            |
| 0.1.1   | 2021-06-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer                                                                               |
| 0.1.0   | 2021-06-21 | [\#4176](https://github.com/airbytehq/airbyte/pull/4176)   | Destination using Typed Struct and Repeated fields                                                                      |
