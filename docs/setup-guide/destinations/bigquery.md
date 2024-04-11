# BigQuery

This page contains the setup guide and reference information for BigQuery.

Setting up the BigQuery destination involves setting up the data loading method (BigQuery Standard method and Google Cloud Storage (GCS) bucket) and configuring the BigQuery destination connector using Daspire.

## Prerequisites

* [A Google Cloud project with BigQuery enabled](https://cloud.google.com/bigquery/docs/quickstarts/query-public-dataset-console)
* [A BigQuery dataset](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui#create_a_dataset) to sync data to

  > **Note:** Queries written in BigQuery can only reference datasets in the same physical location. If you plan on combining the data that Daspire syncs with data from other datasets in your queries, create the datasets in the same location on Google Cloud. For more information, read [Introduction to Datasets](https://cloud.google.com/bigquery/docs/datasets-intro)

* A Google Cloud [Service Account](https://cloud.google.com/iam/docs/service-accounts) with the [BigQuery User](https://cloud.google.com/bigquery/docs/access-control#bigquery) and [BigQuery Data Editor](https://cloud.google.com/bigquery/docs/access-control#bigquery) roles and the [Service Account Key in JSON format](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

## Connection modes

While setting up BigQuery, you can configure it in the following modes:

* **BigQuery** : Produces a normalized output by storing the JSON blob data in \_daspire\_raw\_\* tables and then transforming and normalizing the data into separate tables, potentially exploding nested streams into their own tables if basic normalization is configured.

* **BigQuery (Denormalized)**: Leverages BigQuery capabilities with Structured and Repeated fields to produce a single "big" table per stream. Daspire does not support normalization for this option at this time.

## Setup guide

### Step 1: Set up a data loading method

Although you can load data using BigQuery's [INSERTS](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax), we highly recommend using a [Google Cloud Storage bucket](https://cloud.google.com/storage/docs/introduction).

#### Using a Google Cloud Storage bucket (Recommended)

To use a Google Cloud Storage bucket:

1. [Create a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets) with the Protection Tools set to none or Object versioning. Make sure the bucket does not have a [retention policy](https://cloud.google.com/storage/docs/samples/storage-set-retention-policy).

2. [Create an HMAC key and access ID](https://cloud.google.com/storage/docs/authentication/managing-hmackeys#create).

3. Grant the [Storage Object Admin](https://cloud.google.com/storage/docs/access-control/iam-roles#standard-roles)[role](https://cloud.google.com/storage/docs/access-control/iam-roles#standard-roles) to the Google Cloud [Service Account](https://cloud.google.com/iam/docs/service-accounts).

4. Make sure your Cloud Storage bucket is accessible from the machine running Daspire. The easiest way to verify if Daspire is able to connect to your bucket is via the check connection tool in the UI.

#### Using `INSERT`

You can use BigQuery's [INSERT](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax) statement to upload data directly from your source to BigQuery. While this is faster to set up initially, we strongly recommend not using this option for anything other than a quick demo. Due to the Google BigQuery SDK client limitations, using INSERT is 10x slower than using a Google Cloud Storage bucket, and you may see some failures for big datasets and slow sources (for example, if reading from a source takes more than 10-12 hours).

### Step 2: Set up the BigQuery destination in Daspire

1. Log into your Daspire account.

2. Click **Destinations** and then click **+ New destination**.

3. On the Set up the destination page, select **BigQuery** or **BigQuery (denormalized typed struct)** from the **Destination type** dropdown depending on whether you want to set it up in BigQuery or BigQuery (Denormalized) mode.

4. Enter the name for the BigQuery connection.

5. For **Project ID** , enter your [Google Cloud project ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects).

6. For **Dataset Location** , select the location of your BigQuery dataset.

  **WARNING:** You cannot change the location later.

7. For **Default Dataset ID** , enter the BigQuery [Dataset ID](https://cloud.google.com/bigquery/docs/datasets#create-dataset).

8. For **Loading Method** , select Standard Inserts or GCS Staging.

  **TIP:** We recommend using the GCS Staging option.

9. For **Service Account Key JSON (Required for cloud, optional for open-source)**, enter the Google Cloud [Service Account Key in JSON format](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

10. For **Transformation Query Run Type (Optional)**, select **interactive** to have [BigQuery run interactive query jobs](https://cloud.google.com/bigquery/docs/running-queries#queries) or **batch** to have [BigQuery run batch queries](https://cloud.google.com/bigquery/docs/running-queries#batch).

  **NOTE:** Interactive queries are executed as soon as possible and count towards daily concurrent quotas and limits, while batch queries are executed as soon as idle resources are available in the BigQuery shared resource pool. If BigQuery hasn't started the query within 24 hours, BigQuery changes the job priority to interactive. Batch queries don't count towards your concurrent rate limit, making it easier to start many queries at once.

11. For **Google BigQuery Client Chunk Size (Optional)**, use the default value of 15 MiB. Later, if you see networking or memory management problems with the sync (specifically on the destination), try decreasing the chunk size. In that case, the sync will be slower but more likely to succeed.

## Supported sync modes

The BigQuery destination supports the following sync modes:

* Full Refresh Sync
* Incremental - Append Sync
* Incremental - Deduped History

## Output schema

Daspire outputs each stream into its own table in BigQuery. Each table contains three columns:

* `_daspire_ab_id`: A UUID assigned by Daspire to each event that is processed. The column type in BigQuery is String.

* `_daspire_emitted_at`: A timestamp representing when the event was pulled from the data source. The column type in BigQuery is Timestamp.

* `_daspire_data`: A JSON blob representing the event data. The column type in BigQuery is String.

The output tables in BigQuery are partitioned and clustered by the Time-unit column `_daspire_emitted_at` at a daily granularity. Partitions boundaries are based on UTC time. This is useful to limit the number of partitions scanned when querying these partitioned tables, by using a predicate filter (a WHERE clause). Filters on the partitioning column are used to prune the partitions and reduce the query cost. (The parameter **Require partition filter** is not enabled by Daspire, but you may toggle it by updating the produced tables.)

## BigQuery Naming Conventions

Follow [BigQuery Datasets Naming conventions](https://cloud.google.com/bigquery/docs/datasets#dataset-naming).

Daspire converts any invalid characters into `_` characters when writing data. However, since datasets that begin with `_` are hidden on the BigQuery Explorer panel, Daspire prepends the namespace with n for converted namespaces.

## Data type map

| Daspire type | BigQuery type | BigQuery denormalized type |
| --- | --- | --- |
| `DATE` | `DATE` | `DATE` |
| `STRING (BASE64)` | `STRING` | `STRING` |
| `NUMBER` | `FLOAT` | `FLOAT` |
| `OBJECT` | `STRING` | `RECORD` |
| `STRING` | `STRING` | `STRING` |
| `BOOLEAN` | `BOOLEAN` | `BOOLEAN` |
| `INTEGER` | `INTEGER` | `INTEGER` |
| `STRING (BIG_NUMBER)` | `STRING` | `STRING` |
| `STRING (BIG_INTEGER)` | `STRING` | `STRING` |
| `ARRAY` | `REPEATED` | `REPEATED` |
| `STRING (TIMESTAMP_WITH_TIMEZONE)` | `TIMESTAMP` | `DATETIME` |
| `STRING (TIMESTAMP_WITHOUT_TIMEZONE)` | `TIMESTAMP` | `DATETIME` |

## Troubleshooting permission issues

The service account does not have the proper permissions:

* Make sure the BigQuery service account has BigQuery User and BigQuery Data Editor roles or equivalent permissions as those two roles.

* If the GCS staging mode is selected, ensure the BigQuery service account has the right permissions to the GCS bucket and path or the Cloud Storage Admin role, which includes a superset of the required permissions.

The HMAC key is wrong:

* Make sure the HMAC key is created for the BigQuery service account, and the service account has permission to access the GCS bucket and path.