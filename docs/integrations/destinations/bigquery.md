# BigQuery

Setting up the BigQuery destination connector involves setting up the data loading method (BigQuery Standard method and Google Cloud Storage bucket) and configuring the BigQuery destination connector using the Airbyte UI.

This page guides you through setting up the BigQuery destination connector.

## Prerequisites

- For Airbyte Open Source users using the [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector, [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to version `v0.40.0-alpha` or newer and upgrade your BigQuery connector to version `1.1.14` or newer
- [A Google Cloud project with BigQuery enabled](https://cloud.google.com/bigquery/docs/quickstarts/query-public-dataset-console)
- [A BigQuery dataset](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui#create_a_dataset) to sync data to.

    **Note:** Queries written in BigQuery can only reference datasets in the same physical location. If you plan on combining the data that Airbyte syncs with data from other datasets in your queries, create the datasets in the same location on Google Cloud. For more information, read [Introduction to Datasets](https://cloud.google.com/bigquery/docs/datasets-intro)

- (Required for Airbyte Cloud; Optional for Airbyte Open Source) A Google Cloud [Service Account](https://cloud.google.com/iam/docs/service-accounts) with the [`BigQuery User`](https://cloud.google.com/bigquery/docs/access-control#bigquery) and [`BigQuery Data Editor`](https://cloud.google.com/bigquery/docs/access-control#bigquery) roles and the [Service Account Key in JSON format](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

## Connector modes

While setting up the connector, you can configure it in the following modes:

- **BigQuery**: Produces a normalized output by storing the JSON blob data in `_airbyte_raw_*` tables and then transforming and normalizing the data into separate tables, potentially `exploding` nested streams into their own tables if basic normalization is configured.
- **BigQuery (Denormalized)**: Leverages BigQuery capabilities with Structured and Repeated fields to produce a single "big" table per stream. Airbyte does not support normalization for this option at this time.

## Setup guide

### Step 1: Set up a data loading method

Although you can load data using BigQuery's [`INSERTS`](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax), we highly recommend using a [Google Cloud Storage bucket](https://cloud.google.com/storage/docs/introduction).

#### (Recommended) Using a Google Cloud Storage bucket

To use a Google Cloud Storage bucket:

1. [Create a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets) with the Protection Tools set to `none` or `Object versioning`. Make sure the bucket does not have a [retention policy](https://cloud.google.com/storage/docs/samples/storage-set-retention-policy).
2. [Create an HMAC key and access ID](https://cloud.google.com/storage/docs/authentication/managing-hmackeys#create).
3. Grant the [`Storage Object Admin` role](https://cloud.google.com/storage/docs/access-control/iam-roles#standard-roles) to the Google Cloud [Service Account](https://cloud.google.com/iam/docs/service-accounts).
4. Make sure your Cloud Storage bucket is accessible from the machine running Airbyte. The easiest way to verify if Airbyte is able to connect to your bucket is via the check connection tool in the UI.

Your bucket must be encrypted using a Google-managed encryption key (this is the default setting when creating a new bucket). We currently do not support buckets using customer-managed encryption keys (CMEK). You can view this setting under the "Configuration" tab of your GCS bucket, in the `Encryption type` row.

#### Using `INSERT`

You can use BigQuery's [`INSERT`](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax) statement to upload data directly from your source to BigQuery. While this is faster to set up initially, we strongly recommend not using this option for anything other than a quick demo. Due to the Google BigQuery SDK client limitations, using `INSERT` is 10x slower than using a Google Cloud Storage bucket, and you may see some failures for big datasets and slow sources (For example, if reading from a source takes more than 10-12 hours). For more details, refer to https://github.com/airbytehq/airbyte/issues/3549

### Step 2: Set up the BigQuery connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Destinations** and then click **+ New destination**.
3. On the Set up the destination page, select **BigQuery** or **BigQuery (denormalized typed struct)** from the **Destination type** dropdown depending on whether you want to set up the connector in [BigQuery](#connector-modes) or [BigQuery (Denormalized)](#connector-modes) mode.
4. Enter the name for the BigQuery connector.
5. For **Project ID**, enter your [Google Cloud project ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects).
6. For **Dataset Location**, select the location of your BigQuery dataset.
    :::warning
    You cannot change the location later.
    :::
7. For **Default Dataset ID**, enter the BigQuery [Dataset ID](https://cloud.google.com/bigquery/docs/datasets#create-dataset).
8. For **Loading Method**, select [Standard Inserts](#using-insert) or [GCS Staging](#recommended-using-a-google-cloud-storage-bucket).
    :::tip
    We recommend using the GCS Staging option.
    :::
9. For **Service Account Key JSON (Required for cloud, optional for open-source)**, enter the Google Cloud [Service Account Key in JSON format](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).
10. For **Transformation Query Run Type (Optional)**, select **interactive** to have [BigQuery run interactive query jobs](https://cloud.google.com/bigquery/docs/running-queries#queries) or **batch** to have [BigQuery run batch queries](https://cloud.google.com/bigquery/docs/running-queries#batch).

    :::note
    Interactive queries are executed as soon as possible and count towards daily concurrent quotas and limits, while batch queries are executed as soon as idle resources are available in the BigQuery shared resource pool. If BigQuery hasn't started the query within 24 hours, BigQuery changes the job priority to interactive. Batch queries don't count towards your concurrent rate limit, making it easier to start many queries at once.
    :::

11. For **Google BigQuery Client Chunk Size (Optional)**, use the default value of 15 MiB. Later, if you see networking or memory management problems with the sync (specifically on the destination), try decreasing the chunk size. In that case, the sync will be slower but more likely to succeed.

## Supported sync modes

The BigQuery destination connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh Sync
- Incremental - Append Sync
- Incremental - Deduped History

## Output schema

Airbyte outputs each stream into its own table in BigQuery. Each table contains three columns:

* `_airbyte_ab_id`: A UUID assigned by Airbyte to each event that is processed. The column type in BigQuery is `String`.
* `_airbyte_emitted_at`: A timestamp representing when the event was pulled from the data source. The column type in BigQuery is `Timestamp`.
* `_airbyte_data`: A JSON blob representing the event data. The column type in BigQuery is `String`.

The output tables in BigQuery are partitioned and clustered by the Time-unit column `_airbyte_emitted_at` at a daily granularity. Partitions boundaries are based on UTC time.
This is useful to limit the number of partitions scanned when querying these partitioned tables, by using a predicate filter (a `WHERE` clause). Filters on the partitioning column are used to prune the partitions and reduce the query cost. (The parameter **Require partition filter** is not enabled by Airbyte, but you may toggle it by updating the produced tables.)

## BigQuery Naming Conventions

Follow [BigQuery Datasets Naming conventions](https://cloud.google.com/bigquery/docs/datasets#dataset-naming).

Airbyte converts any invalid characters into `_` characters when writing data. However, since datasets that begin with `_` are hidden on the BigQuery Explorer panel, Airbyte prepends the namespace with `n` for converted namespaces.

## Data type map

| Airbyte type                        | BigQuery type | BigQuery denormalized type |
|:------------------------------------|:--------------|:---------------------------|
| DATE                                | DATE          | DATE                       |
| STRING (BASE64)                     | STRING        | STRING                     |
| NUMBER                              | FLOAT         | NUMBER                     |
| OBJECT                              | STRING        | RECORD                     |
| STRING                              | STRING        | STRING                     |
| BOOLEAN                             | BOOLEAN       | BOOLEAN                    |
| INTEGER                             | INTEGER       | INTEGER                    |
| STRING (BIG_NUMBER)                 | STRING        | STRING                     |
| STRING (BIG_INTEGER)                | STRING        | STRING                     |
| ARRAY                               | REPEATED      | REPEATED                   |
| STRING (TIMESTAMP_WITH_TIMEZONE)    | TIMESTAMP     | DATETIME                   |
| STRING (TIMESTAMP_WITHOUT_TIMEZONE) | TIMESTAMP     | DATETIME                   |

## Troubleshooting permission issues

The service account does not have the proper permissions.

- Make sure the BigQuery service account has `BigQuery User` and `BigQuery Data Editor` roles or equivalent permissions as those two roles.
- If the GCS staging mode is selected, ensure the BigQuery service account has the right permissions to the GCS bucket and path or the `Cloud Storage Admin` role, which includes a superset of the required permissions.

The HMAC key is wrong.

- Make sure the HMAC key is created for the BigQuery service account, and the service account has permission to access the GCS bucket and path.

## Tutorials

Now that you have set up the BigQuery destination connector, check out the following BigQuery tutorials:

- [Export Google Analytics data to BigQuery](https://airbyte.com/tutorials/export-google-analytics-to-bigquery)
- [Load data from Facebook Ads to BigQuery](https://airbyte.com/tutorials/facebook-ads-to-bigquery)
- [Replicate Salesforce data to BigQuery](https://airbyte.com/tutorials/replicate-salesforce-data-to-bigquery)
- [Partition and cluster BigQuery tables with Airbyte and dbt](https://airbyte.com/tutorials/bigquery-partition-cluster)


## Changelog

### bigquery

| Version | Date       | Pull Request                                              | Subject                                                                                                                  |
|:--------|:-----------|:----------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|
| 1.2.13  | 2023-01-26 | [#20631](https://github.com/airbytehq/airbyte/pull/20631) | Added support for destination checkpointing with staging                                                                 |
| 1.2.12  | 2023-01-18 | [#21087](https://github.com/airbytehq/airbyte/pull/21087) | Wrap Authentication Errors as Config Exceptions                                                                          |
| 1.2.11  | 2023-01-18 | [#21144](https://github.com/airbytehq/airbyte/pull/21144) | Added explicit error message if sync fails due to a config issue                                                         |
| 1.2.9   | 2022-12-14 | [#20501](https://github.com/airbytehq/airbyte/pull/20501) | Report GCS staging failures that occur during connection check                                                           |
| 1.2.8   | 2022-11-22 | [#19489](https://github.com/airbytehq/airbyte/pull/19489) | Added non-billable projects handle to check connection stage                                                             |
| 1.2.7   | 2022-11-11 | [#19358](https://github.com/airbytehq/airbyte/pull/19358) | Fixed check method to capture mismatch dataset location                                                                  |
| 1.2.6   | 2022-11-10 | [#18554](https://github.com/airbytehq/airbyte/pull/18554) | Improve check connection method to handle more errors                                                                    |
| 1.2.5   | 2022-10-19 | [#18162](https://github.com/airbytehq/airbyte/pull/18162) | Improve error logs                                                                                                       |
| 1.2.4   | 2022-09-26 | [#16890](https://github.com/airbytehq/airbyte/pull/16890) | Add user-agent header                                                                                                    |
| 1.2.3   | 2022-09-22 | [#17054](https://github.com/airbytehq/airbyte/pull/17054) | Respect stream namespace                                                                                                 |
| 1.2.1   | 2022-09-14 | [#15668](https://github.com/airbytehq/airbyte/pull/15668) | (bugged, do not use) Wrap logs in AirbyteLogMessage                                                                      |
| 1.2.0   | 2022-09-09 | [#14023](https://github.com/airbytehq/airbyte/pull/14023) | (bugged, do not use) Cover arrays only if they are nested                                                                |
| 1.1.16  | 2022-09-01 | [#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields) |
| 1.1.15  | 2022-08-22 | [15787](https://github.com/airbytehq/airbyte/pull/15787)  | Throw exception if job failed                                                                                            |
| 1.1.14  | 2022-08-03 | [14784](https://github.com/airbytehq/airbyte/pull/14784)  | Enabling Application Default Credentials                                                                                 |
| 1.1.13  | 2022-08-02 | [14801](https://github.com/airbytehq/airbyte/pull/14801)  | Fix multiple log bindings                                                                                                |
| 1.1.12  | 2022-08-02 | [15180](https://github.com/airbytehq/airbyte/pull/15180)  | Fix standard loading mode                                                                                                |
| 1.1.11  | 2022-06-24 | [14114](https://github.com/airbytehq/airbyte/pull/14114)  | Remove "additionalProperties": false from specs for connectors with staging                                              |
| 1.1.10  | 2022-06-16 | [13852](https://github.com/airbytehq/airbyte/pull/13852)  | Updated stacktrace format for any trace message errors                                                                   |
| 1.1.9   | 2022-06-17 | [13753](https://github.com/airbytehq/airbyte/pull/13753)  | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                  |
| 1.1.8   | 2022-06-07 | [13579](https://github.com/airbytehq/airbyte/pull/13579)  | Always check GCS bucket for GCS loading method to catch invalid HMAC keys.                                               |
| 1.1.7   | 2022-06-07 | [13424](https://github.com/airbytehq/airbyte/pull/13424)  | Reordered fields for specification.                                                                                      |
| 1.1.6   | 2022-05-15 | [12768](https://github.com/airbytehq/airbyte/pull/12768)  | Clarify that the service account key json field is required on cloud.                                                    |
| 1.1.5   | 2022-05-12 | [12805](https://github.com/airbytehq/airbyte/pull/12805)  | Updated to latest base-java to emit AirbyteTraceMessage on error.                                                        |
| 1.1.4   | 2022-05-04 | [12578](https://github.com/airbytehq/airbyte/pull/12578)  | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                          |
| 1.1.3   | 2022-05-02 | [12528](https://github.com/airbytehq/airbyte/pull/12528)  | Update Dataset location field description                                                                                |
| 1.1.2   | 2022-04-29 | [12477](https://github.com/airbytehq/airbyte/pull/12477)  | Dataset location is a required field                                                                                     |
| 1.1.1   | 2022-04-15 | [12068](https://github.com/airbytehq/airbyte/pull/12068)  | Fixed bug with GCS bucket conditional binding                                                                            |
| 1.1.0   | 2022-04-06 | [11776](https://github.com/airbytehq/airbyte/pull/11776)  | Use serialized buffering strategy to reduce memory consumption.                                                          |
| 1.0.2   | 2022-03-30 | [11620](https://github.com/airbytehq/airbyte/pull/11620)  | Updated spec                                                                                                             |
| 1.0.1   | 2022-03-24 | [11350](https://github.com/airbytehq/airbyte/pull/11350)  | Improve check performance                                                                                                |
| 1.0.0   | 2022-03-18 | [11238](https://github.com/airbytehq/airbyte/pull/11238)  | Updated spec and documentation                                                                                           |
| 0.6.12  | 2022-03-18 | [10793](https://github.com/airbytehq/airbyte/pull/10793)  | Fix namespace with invalid characters                                                                                    |
| 0.6.11  | 2022-03-03 | [10755](https://github.com/airbytehq/airbyte/pull/10755)  | Make sure to kill children threads and stop JVM                                                                          |
| 0.6.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)  | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                             |
| 0.6.6   | 2022-02-01 | [9959](https://github.com/airbytehq/airbyte/pull/9959)    | Fix null pointer exception from buffered stream consumer.                                                                |
| 0.6.6   | 2022-01-29 | [9745](https://github.com/airbytehq/airbyte/pull/9745)    | Integrate with Sentry.                                                                                                   |
| 0.6.5   | 2022-01-18 | [9573](https://github.com/airbytehq/airbyte/pull/9573)    | BigQuery Destination : update description for some input fields                                                          |
| 0.6.4   | 2022-01-17 | [8383](https://github.com/airbytehq/airbyte/issues/8383)  | Support dataset-id prefixed by project-id                                                                                |
| 0.6.3   | 2022-01-12 | [9415](https://github.com/airbytehq/airbyte/pull/9415)    | BigQuery Destination : Fix GCS processing of Facebook data                                                               |
| 0.6.2   | 2022-01-10 | [9121](https://github.com/airbytehq/airbyte/pull/9121)    | Fixed check method for GCS mode to verify if all roles assigned to user                                                  |
| 0.6.1   | 2021-12-22 | [9039](https://github.com/airbytehq/airbyte/pull/9039)    | Added part_size configuration to UI for GCS staging                                                                      |
| 0.6.0   | 2021-12-17 | [8788](https://github.com/airbytehq/airbyte/issues/8788)  | BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files                              |
| 0.5.1   | 2021-12-16 | [8816](https://github.com/airbytehq/airbyte/issues/8816)  | Update dataset locations                                                                                                 |
| 0.5.0   | 2021-10-26 | [7240](https://github.com/airbytehq/airbyte/issues/7240)  | Output partitioned/clustered tables                                                                                      |
| 0.4.1   | 2021-10-04 | [6733](https://github.com/airbytehq/airbyte/issues/6733)  | Support dataset starting with numbers                                                                                    |
| 0.4.0   | 2021-08-26 | [5296](https://github.com/airbytehq/airbyte/issues/5296)  | Added GCS Staging uploading option                                                                                       |
| 0.3.12  | 2021-08-03 | [3549](https://github.com/airbytehq/airbyte/issues/3549)  | Add optional arg to make a possibility to change the BigQuery client's chunk\buffer size                                 |
| 0.3.11  | 2021-07-30 | [5125](https://github.com/airbytehq/airbyte/pull/5125)    | Enable `additionalPropertities` in spec.json                                                                             |
| 0.3.10  | 2021-07-28 | [3549](https://github.com/airbytehq/airbyte/issues/3549)  | Add extended logs and made JobId filled with region and projectId                                                        |
| 0.3.9   | 2021-07-28 | [5026](https://github.com/airbytehq/airbyte/pull/5026)    | Add sanitized json fields in raw tables to handle quotes in column names                                                 |
| 0.3.6   | 2021-06-18 | [3947](https://github.com/airbytehq/airbyte/issues/3947)  | Service account credentials are now optional.                                                                            |
| 0.3.4   | 2021-06-07 | [3277](https://github.com/airbytehq/airbyte/issues/3277)  | Add dataset location option                                                                                              |

### bigquery-denormalized

| Version | Date       | Pull Request                                              | Subject                                                                                                                  |
|:--------|:-----------|:----------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|
| 1.2.11  | 2023-01-18 | [#21144](https://github.com/airbytehq/airbyte/pull/21144) | Added explicit error message if sync fails due to a config issue                                                         |
| 1.2.10  | 2023-01-04 | [#20730](https://github.com/airbytehq/airbyte/pull/20730) | An incoming source Number type will create a big query integer rather than a float.                                      |
| 1.2.9   | 2022-12-14 | [#20501](https://github.com/airbytehq/airbyte/pull/20501) | Report GCS staging failures that occur during connection check                                                           |
| 1.2.8   | 2022-11-22 | [#19489](https://github.com/airbytehq/airbyte/pull/19489) | Added non-billable projects handle to check connection stage                                                             |
| 1.2.7   | 2022-11-11 | [#19358](https://github.com/airbytehq/airbyte/pull/19358) | Fixed check method to capture mismatch dataset location                                                                  |
| 1.2.6   | 2022-11-10 | [#18554](https://github.com/airbytehq/airbyte/pull/18554) | Improve check connection method to handle more errors                                                                    |
| 1.2.5   | 2022-10-19 | [#18162](https://github.com/airbytehq/airbyte/pull/18162) | Improve error logs                                                                                                       |
| 1.2.4   | 2022-09-26 | [#16890](https://github.com/airbytehq/airbyte/pull/16890) | Add user-agent header                                                                                                    |
| 1.2.3   | 2022-09-22 | [#17054](https://github.com/airbytehq/airbyte/pull/17054) | Respect stream namespace                                                                                                 |
| 1.2.2   | 2022-09-14 | [15668](https://github.com/airbytehq/airbyte/pull/15668)  | (bugged, do not use) Wrap logs in AirbyteLogMessage                                                                      |
| 1.2.1   | 2022-09-10 | [16401](https://github.com/airbytehq/airbyte/pull/16401)  | (bugged, do not use) Wrapping string objects with TextNode                                                               |
| 1.2.0   | 2022-09-09 | [#14023](https://github.com/airbytehq/airbyte/pull/14023) | (bugged, do not use) Cover arrays only if they are nested                                                                |
| 1.1.16  | 2022-09-01 | [#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields) |
| 1.1.15  | 2022-08-03 | [14784](https://github.com/airbytehq/airbyte/pull/14784)  | Enabling Application Default Credentials                                                                                 |
| 1.1.14  | 2022-08-02 | [14801](https://github.com/airbytehq/airbyte/pull/14801)  | Fix multiple log bindings                                                                                                |
| 1.1.13  | 2022-08-02 | [15180](https://github.com/airbytehq/airbyte/pull/15180)  | Fix standard loading mode                                                                                                |
| 1.1.12  | 2022-06-29 | [14079](https://github.com/airbytehq/airbyte/pull/14079)  | Map "airbyte_type": "big_integer" to INT64                                                                               |
| 1.1.11  | 2022-06-24 | [14114](https://github.com/airbytehq/airbyte/pull/14114)  | Remove "additionalProperties": false from specs for connectors with staging                                              |
| 1.1.10  | 2022-06-16 | [13852](https://github.com/airbytehq/airbyte/pull/13852)  | Updated stacktrace format for any trace message errors                                                                   |
| 1.1.9   | 2022-06-17 | [13753](https://github.com/airbytehq/airbyte/pull/13753)  | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                  |
| 1.1.8   | 2022-06-07 | [13579](https://github.com/airbytehq/airbyte/pull/13579)  | Always check GCS bucket for GCS loading method to catch invalid HMAC keys.                                               |
| 1.1.7   | 2022-06-07 | [13424](https://github.com/airbytehq/airbyte/pull/13424)  | Reordered fields for specification.                                                                                      |
| 1.1.6   | 2022-05-15 | [12768](https://github.com/airbytehq/airbyte/pull/12768)  | Clarify that the service account key json field is required on cloud.                                                    |
| 0.3.5   | 2022-05-12 | [12805](https://github.com/airbytehq/airbyte/pull/12805)  | Updated to latest base-java to emit AirbyteTraceMessage on error.                                                        |
| 0.3.4   | 2022-05-04 | [12578](https://github.com/airbytehq/airbyte/pull/12578)  | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                          |
| 0.3.3   | 2022-05-02 | [12528](https://github.com/airbytehq/airbyte/pull/12528)  | Update Dataset location field description                                                                                |
| 0.3.2   | 2022-04-29 | [12477](https://github.com/airbytehq/airbyte/pull/12477)  | Dataset location is a required field                                                                                     |
| 0.3.1   | 2022-04-15 | [11978](https://github.com/airbytehq/airbyte/pull/11978)  | Fixed emittedAt timestamp.                                                                                               |
| 0.3.0   | 2022-04-06 | [11776](https://github.com/airbytehq/airbyte/pull/11776)  | Use serialized buffering strategy to reduce memory consumption.                                                          |
| 0.2.15  | 2022-04-05 | [11166](https://github.com/airbytehq/airbyte/pull/11166)  | Fixed handling of anyOf and allOf fields                                                                                 |
| 0.2.14  | 2022-04-02 | [11620](https://github.com/airbytehq/airbyte/pull/11620)  | Updated spec                                                                                                             |
| 0.2.13  | 2022-04-01 | [11636](https://github.com/airbytehq/airbyte/pull/11636)  | Added new unit tests                                                                                                     |
| 0.2.12  | 2022-03-28 | [11454](https://github.com/airbytehq/airbyte/pull/11454)  | Integration test enhancement for picking test-data and schemas                                                           |
| 0.2.11  | 2022-03-18 | [10793](https://github.com/airbytehq/airbyte/pull/10793)  | Fix namespace with invalid characters                                                                                    |
| 0.2.10  | 2022-03-03 | [10755](https://github.com/airbytehq/airbyte/pull/10755)  | Make sure to kill children threads and stop JVM                                                                          |
| 0.2.8   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)  | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                             |
| 0.2.7   | 2022-02-01 | [9959](https://github.com/airbytehq/airbyte/pull/9959)    | Fix null pointer exception from buffered stream consumer.                                                                |
| 0.2.6   | 2022-01-29 | [9745](https://github.com/airbytehq/airbyte/pull/9745)    | Integrate with Sentry.                                                                                                   |
| 0.2.5   | 2022-01-18 | [9573](https://github.com/airbytehq/airbyte/pull/9573)    | BigQuery Destination : update description for some input fields                                                          |
| 0.2.4   | 2022-01-17 | [8383](https://github.com/airbytehq/airbyte/issues/8383)  | BigQuery/BiqQuery denorm Destinations : Support dataset-id prefixed by project-id                                        |
| 0.2.3   | 2022-01-12 | [9415](https://github.com/airbytehq/airbyte/pull/9415)    | BigQuery Destination : Fix GCS processing of Facebook data                                                               |
| 0.2.2   | 2021-12-22 | [9039](https://github.com/airbytehq/airbyte/pull/9039)    | Added part_size configuration to UI for GCS staging                                                                      |
| 0.2.1   | 2021-12-21 | [8574](https://github.com/airbytehq/airbyte/pull/8574)    | Added namespace to Avro and Parquet record types                                                                         |
| 0.2.0   | 2021-12-17 | [8788](https://github.com/airbytehq/airbyte/pull/8788)    | BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files                              |
| 0.1.11  | 2021-12-16 | [8816](https://github.com/airbytehq/airbyte/issues/8816)  | Update dataset locations                                                                                                 |
| 0.1.10  | 2021-11-09 | [7804](https://github.com/airbytehq/airbyte/pull/7804)    | handle null values in fields described by a $ref definition                                                              |
| 0.1.9   | 2021-11-08 | [7736](https://github.com/airbytehq/airbyte/issues/7736)  | Fixed the handling of ObjectNodes with $ref definition key                                                               |
| 0.1.8   | 2021-10-27 | [7413](https://github.com/airbytehq/airbyte/issues/7413)  | Fixed DATETIME conversion for BigQuery                                                                                   |
| 0.1.7   | 2021-10-26 | [7240](https://github.com/airbytehq/airbyte/issues/7240)  | Output partitioned/clustered tables                                                                                      |
| 0.1.6   | 2021-09-16 | [6145](https://github.com/airbytehq/airbyte/pull/6145)    | BigQuery Denormalized support for date, datetime & timestamp types through the json "format" key                         |
| 0.1.5   | 2021-09-07 | [5881](https://github.com/airbytehq/airbyte/pull/5881)    | BigQuery Denormalized NPE fix                                                                                            |
| 0.1.4   | 2021-09-04 | [5813](https://github.com/airbytehq/airbyte/pull/5813)    | fix Stackoverflow error when receive a schema from source where "Array" type doesn't contain a required "items" element  |
| 0.1.3   | 2021-08-07 | [5261](https://github.com/airbytehq/airbyte/pull/5261)    | 🐛 Destination BigQuery\(Denormalized\): Fix processing arrays of records                                                |
| 0.1.2   | 2021-07-30 | [5125](https://github.com/airbytehq/airbyte/pull/5125)    | Enable `additionalPropertities` in spec.json                                                                             |
| 0.1.1   | 2021-06-21 | [3555](https://github.com/airbytehq/airbyte/pull/3555)    | Partial Success in BufferedStreamConsumer                                                                                |
| 0.1.0   | 2021-06-21 | [4176](https://github.com/airbytehq/airbyte/pull/4176)    | Destination using Typed Struct and Repeated fields                                                                       |
