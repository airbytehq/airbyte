# BigQuery

Setting up the BigQuery destination connector involves setting up the data loading method and configuring the BigQuery destination connector
using the Airbyte UI.

This page guides you through setting up the BigQuery destination connector.

## Prerequisites

- For Airbyte Open Source users using the
  [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector,
  [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to
  version `v0.40.0-alpha` or newer and upgrade your BigQuery connector to version `1.1.14` or newer
- [A Google Cloud project with BigQuery enabled](https://cloud.google.com/bigquery/docs/quickstarts/query-public-dataset-console)
- [A BigQuery dataset](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui#create_a_dataset)
  to sync data to.

  **Note:** Queries written in BigQuery can only reference datasets in the same physical location.
  If you plan on combining the data that Airbyte syncs with data from other datasets in your
  queries, create the datasets in the same location on Google Cloud. For more information, read
  [Introduction to Datasets](https://cloud.google.com/bigquery/docs/datasets-intro)

- (Required for Airbyte Cloud; Optional for Airbyte Open Source) A Google Cloud
  [Service Account](https://cloud.google.com/iam/docs/service-accounts) with the
  [`BigQuery User`](https://cloud.google.com/bigquery/docs/access-control#bigquery) and
  [`BigQuery Data Editor`](https://cloud.google.com/bigquery/docs/access-control#bigquery) roles and
  the
  [Service Account Key in JSON format](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

## Setup guide

### Step 1: Set up a data loading method

#### Using Batched Standard Inserts

You can use the BigQuery driver's built-in conversion to take `INSERT` statements and convert that to file uploads which are then loaded into BigQuery in batches. This is the simplest way to load data into BigQuery in a performant way. These staging files are managed by BigQuery and deleted automatically after the load is complete.

#### Using a Google Cloud Storage bucket

If you want more control of how and where your staging files are stored, you can opt to use a GCS bucket.

To use a Google Cloud Storage bucket:

1. [Create a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets) with the
   Protection Tools set to `none` or `Object versioning`. Make sure the bucket does not have a
   [retention policy](https://cloud.google.com/storage/docs/samples/storage-set-retention-policy).
2. [Create an HMAC key and access ID](https://cloud.google.com/storage/docs/authentication/managing-hmackeys#create).
3. Grant the
   [`Storage Object Admin` role](https://cloud.google.com/storage/docs/access-control/iam-roles#standard-roles)
   to the Google Cloud [Service Account](https://cloud.google.com/iam/docs/service-accounts). This
   must be the same service account as the one you configure for BigQuery access in the
   [BigQuery connector setup step](#step-2-set-up-the-bigquery-connector).
4. Make sure your Cloud Storage bucket is accessible from the machine running Airbyte. The easiest
   way to verify if Airbyte is able to connect to your bucket is via the check connection tool in
   the UI.

Your bucket must be encrypted using a Google-managed encryption key (this is the default setting
when creating a new bucket). We currently do not support buckets using customer-managed encryption
keys (CMEK). You can view this setting under the "Configuration" tab of your GCS bucket, in the
`Encryption type` row.

### Step 2: Set up the BigQuery connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source
   account.
2. Click **Destinations** and then click **+ New destination**.
3. On the Set up the destination page, select **BigQuery** from the **Destination type** dropdown.
4. Enter the name for the BigQuery connector.
5. For **Project ID**, enter your
   [Google Cloud project ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects).
6. For **Dataset Location**, select the location of your BigQuery dataset.

:::warning
You cannot change the location later.
:::

7. For **Default Dataset ID**, enter the BigQuery
   [Dataset ID](https://cloud.google.com/bigquery/docs/datasets#create-dataset).
8. For **Loading Method**, select [Batched Standard Inserts](#using-batched-standard-inserts) or
   [GCS Staging](#using-a-google-cloud-storage-bucket).
9. For **Service Account Key JSON (Required for cloud, optional for open-source)**, enter the Google
   Cloud
   [Service Account Key in JSON format](https://cloud.google.com/iam/docs/creating-managing-service-account-keys).

:::note
Be sure to copy all contents in the Account Key JSON file including the brackets.
:::

11. For **Transformation Query Run Type (Optional)**, select **interactive** to have
    [BigQuery run interactive query jobs](https://cloud.google.com/bigquery/docs/running-queries#queries)
    or **batch** to have
    [BigQuery run batch queries](https://cloud.google.com/bigquery/docs/running-queries#batch).

:::note
Interactive queries are executed as soon as possible and count towards daily concurrent
quotas and limits, while batch queries are executed as soon as idle resources are available in
the BigQuery shared resource pool. If BigQuery hasn't started the query within 24 hours,
BigQuery changes the job priority to interactive. Batch queries don't count towards your
concurrent rate limit, making it easier to start many queries at once.
:::

11. For **Google BigQuery Client Chunk Size (Optional)**, use the default value of 15 MiB. Later, if
    you see networking or memory management problems with the sync (specifically on the
    destination), try decreasing the chunk size. In that case, the sync will be slower but more
    likely to succeed.

## Supported sync modes

The BigQuery destination connector supports the following
[sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh Sync
- Incremental - Append Sync
- Incremental - Append + Deduped

## Output schema

Airbyte outputs each stream into its own raw table in `airbyte_internal` dataset by default (can be
overriden by user) and a final table with Typed columns. Contents in raw table are _NOT_
deduplicated.

### Raw Table schema

| Airbyte field          | Description                                                        | Column type |
| ---------------------- | ------------------------------------------------------------------ | ----------- |
| \_airbyte_raw_id       | A UUID assigned to each processed event                            | STRING      |
| \_airbyte_extracted_at | A timestamp for when the event was pulled from the data source     | TIMESTAMP   |
| \_airbyte_loaded_at    | Timestamp to indicate when the record was loaded into Typed tables | TIMESTAMP   |
| \_airbyte_data         | A JSON blob with the event data.                                   | STRING      |

**Note:** Although the contents of the `_airbyte_data` are fairly stable, schema of the raw table
could be subject to change in future versions.

### Final Table schema

- `airbyte_raw_id`: A UUID assigned by Airbyte to each event that is processed. The column type in
  BigQuery is `String`.
- `airbyte_extracted_at`: A timestamp representing when the event was pulled from the data source.
  The column type in BigQuery is `Timestamp`.
- `_airbyte_meta`: A JSON blob representing typing errors. You can query these results to audit
  misformatted or unexpected data. The column type in BigQuery is `JSON`. ... and a column of the
  proper data type for each of the top-level properties from your source's schema. Arrays and
  Objects will remain as JSON columns in BigQuery. Learn more about Typing and Deduping
  [here](/using-airbyte/core-concepts/typing-deduping)

The output tables in BigQuery are partitioned by the Time-unit column `airbyte_extracted_at` at a
daily granularity and clustered by `airbyte_extracted_at` and the table Primary Keys. Partitions
boundaries are based on UTC time. This is useful to limit the number of partitions scanned when
querying these partitioned tables, by using a predicate filter (a `WHERE` clause). Filters on the
partitioning column are used to prune the partitions and reduce the query cost. (The parameter
**Require partition filter** is not enabled by Airbyte, but you may toggle it by updating the
produced tables.)

## BigQuery Naming Conventions

Follow
[BigQuery Datasets Naming conventions](https://cloud.google.com/bigquery/docs/datasets#dataset-naming).

Airbyte converts any invalid characters into `_` characters when writing data. However, since
datasets that begin with `_` are hidden on the BigQuery Explorer panel, Airbyte prepends the
namespace with `n` for converted namespaces.

## Data type map

| Airbyte type                        | BigQuery type |
| :---------------------------------- | :------------ |
| STRING                              | STRING        |
| STRING (BASE64)                     | STRING        |
| STRING (BIG_NUMBER)                 | STRING        |
| STRING (BIG_INTEGER)                | STRING        |
| NUMBER                              | NUMERIC       |
| INTEGER                             | INT64         |
| BOOLEAN                             | BOOL          |
| STRING (TIMESTAMP_WITH_TIMEZONE)    | TIMESTAMP     |
| STRING (TIMESTAMP_WITHOUT_TIMEZONE) | DATETIME      |
| STRING (TIME_WITH_TIMEZONE)         | STRING        |
| STRING (TIME_WITHOUT_TIMEZONE)      | TIME          |
| DATE                                | DATE          |
| OBJECT                              | JSON          |
| ARRAY                               | JSON          |

## Troubleshooting permission issues

The service account does not have the proper permissions.

- Make sure the BigQuery service account has `BigQuery User` and `BigQuery Data Editor` roles or
  equivalent permissions as those two roles.
- If the GCS staging mode is selected, ensure the BigQuery service account has the right permissions
  to the GCS bucket and path or the `Cloud Storage Admin` role, which includes a superset of the
  required permissions.

The HMAC key is wrong.

- Make sure the HMAC key is created for the BigQuery service account, and the service account has
  permission to access the GCS bucket and path.

## Tutorials

Now that you have set up the BigQuery destination connector, check out the following BigQuery
tutorials:

- [Export Google Analytics data to BigQuery](https://airbyte.com/tutorials/export-google-analytics-to-bigquery)
- [Load data from Facebook Ads to BigQuery](https://airbyte.com/tutorials/facebook-ads-to-bigquery)
- [Replicate Salesforce data to BigQuery](https://airbyte.com/tutorials/replicate-salesforce-data-to-bigquery)
- [Partition and cluster BigQuery tables with Airbyte and dbt](https://airbyte.com/tutorials/bigquery-partition-cluster)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                                                                          |
| :------ | :--------- | :--------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2.8.9   | 2024-08-20 | [44476](https://github.com/airbytehq/airbyte/pull/44476)   | Increase message parsing limit to 100mb                                                                                                                                          |
| 2.8.8   | 2024-08-22 | [44526](https://github.com/airbytehq/airbyte/pull/44526)   | Revert protocol compliance fix                                                                                                                                                   |
| 2.8.7   | 2024-08-15 | [42504](https://github.com/airbytehq/airbyte/pull/42504)   | Fix bug in refreshes logic (already mitigated in platform, just fixing protocol compliance)                                                                                      |
| 2.8.6   | 2024-07-30 | [42511](https://github.com/airbytehq/airbyte/pull/42511)   | Added a copy operation to validate copy permissions in the check function                                                                                                        |
| 2.8.5   | 2024-07-22 | [42407](https://github.com/airbytehq/airbyte/pull/42407)   | Batched Standard Inserts is default loading mode                                                                                                                                 |
| 2.8.4   | 2024-07-15 | [41968](https://github.com/airbytehq/airbyte/pull/41968)   | Don't hang forever on empty stream list; shorten error message on INCOMPLETE stream status                                                                                       |
| 2.8.3   | 2024-07-12 | [41674](https://github.com/airbytehq/airbyte/pull/41674)   | Upgrade to latest CDK                                                                                                                                                            |
| 2.8.2   | 2024-07-08 | [41041](https://github.com/airbytehq/airbyte/pull/41041)   | Fix resume logic in truncate refreshes to prevent data loss                                                                                                                      |
| 2.8.1   | 2024-06-25 | [39379](https://github.com/airbytehq/airbyte/pull/39379)   | Removing requirement of a redundant permission bigquery.datasets.create permission                                                                                               |
| 2.8.0   | 2024-06-21 | [39904](https://github.com/airbytehq/airbyte/pull/39904)   | Convert all production code to kotlin                                                                                                                                            |
| 2.7.1   | 2024-06-17 | [39526](https://github.com/airbytehq/airbyte/pull/39526)   | Internal code change for improved error reporting in case of source/platform failure (`INCOMPLETE` stream status / empty ConfiguredCatalog).                                     |
| 2.7.0   | 2024-06-17 | [38713](https://github.com/airbytehq/airbyte/pull/38713)   | Support for [refreshes](../../operator-guides/refreshes.md) and resumable full refresh. WARNING: You must upgrade to platform 0.63.7 before upgrading to this connector version. |
| 2.6.3   | 2024-06-10 | [38331](https://github.com/airbytehq/airbyte/pull/38331)   | Internal code changes in preparation for future feature release                                                                                                                  |
| 2.6.2   | 2024-06-07 | [38764](https://github.com/airbytehq/airbyte/pull/38764)   | Increase message length limit to 50MiB                                                                                                                                           |
| 2.6.1   | 2024-05-29 | [38770](https://github.com/airbytehq/airbyte/pull/38770)   | Internal code change (switch to CDK artifact)                                                                                                                                    |
| 2.6.0   | 2024-05-28 | [38359](https://github.com/airbytehq/airbyte/pull/38359)   | Propagate airbyte_meta from sources; add generation_id column                                                                                                                    |
| 2.5.1   | 2024-05-22 | [38591](https://github.com/airbytehq/airbyte/pull/38591)   | Bugfix to include forward-slash when cleaning up stage                                                                                                                           |
| 2.5.0   | 2024-05-22 | [38132](https://github.com/airbytehq/airbyte/pull/38132)   | Major rewrite of existing code, Adapting to CDK changes introduced in [38107](https://github.com/airbytehq/airbyte/pull/38107)                                                   |
| 2.4.20  | 2024-05-13 | [38131](https://github.com/airbytehq/airbyte/pull/38131)   | Cleanup `BigQueryWriteConfig` and reuse `StreamConfig`; Adapt to `StreamConfig` signature changes                                                                                |
| 2.4.19  | 2024-05-10 | [38125](https://github.com/airbytehq/airbyte/pull/38125)   | adopt latest CDK code                                                                                                                                                            |
| 2.4.18  | 2024-05-10 | [38111](https://github.com/airbytehq/airbyte/pull/38111)   | No functional changes, deleting unused code                                                                                                                                      |
| 2.4.17  | 2024-05-09 | [38098](https://github.com/airbytehq/airbyte/pull/38098)   | Internal build structure change                                                                                                                                                  |
| 2.4.16  | 2024-05-08 | [37714](https://github.com/airbytehq/airbyte/pull/37714)   | Adopt CDK 0.34.0                                                                                                                                                                 |
| 2.4.15  | 2024-05-07 | [34611](https://github.com/airbytehq/airbyte/pull/34611)   | Adopt CDK 0.33.2                                                                                                                                                                 |
| 2.4.14  | 2024-02-25 | [37584](https://github.com/airbytehq/airbyte/pull/37584)   | Remove unused insecure dependencies from CDK                                                                                                                                     |
| 2.4.13  | 2024-02-25 | [36899](https://github.com/airbytehq/airbyte/pull/36899)   | adopt latest CDK                                                                                                                                                                 |
| 2.4.12  | 2024-03-04 | [35315](https://github.com/airbytehq/airbyte/pull/35315)   | Adopt CDK 0.23.11                                                                                                                                                                |
| 2.4.11  | 2024-02-22 | [35569](https://github.com/airbytehq/airbyte/pull/35569)   | Fix logging bug.                                                                                                                                                                 |
| 2.4.10  | 2024-02-15 | [35240](https://github.com/airbytehq/airbyte/pull/35240)   | Adopt CDK 0.20.9                                                                                                                                                                 |
| 2.4.9   | 2024-02-15 | [35285](https://github.com/airbytehq/airbyte/pull/35285)   | Adopt CDK 0.20.8                                                                                                                                                                 |
| 2.4.8   | 2024-02-12 | [35144](https://github.com/airbytehq/airbyte/pull/35144)   | Adopt CDK 0.20.2                                                                                                                                                                 |
| 2.4.7   | 2024-02-12 | [35111](https://github.com/airbytehq/airbyte/pull/35111)   | Adopt CDK 0.20.1                                                                                                                                                                 |
| 2.4.6   | 2024-02-09 | [34575](https://github.com/airbytehq/airbyte/pull/34575)   | Adopt CDK 0.20.0                                                                                                                                                                 |
| 2.4.5   | 2024-02-08 | [34745](https://github.com/airbytehq/airbyte/pull/34745)   | Adopt CDK 0.19.0                                                                                                                                                                 |
| 2.4.4   | 2024-02-08 | [35027](https://github.com/airbytehq/airbyte/pull/35027)   | Upgrade CDK to 0.17.1                                                                                                                                                            |
| 2.4.3   | 2024-02-01 | [34728](https://github.com/airbytehq/airbyte/pull/34728)   | Upgrade CDK to 0.16.4; Notable changes from 0.14.2, 0.15.1 and 0.16.3                                                                                                            |
| 2.4.2   | 2024-01-24 | [34451](https://github.com/airbytehq/airbyte/pull/34451)   | Improve logging for unparseable input                                                                                                                                            |
| 2.4.1   | 2024-01-24 | [34458](https://github.com/airbytehq/airbyte/pull/34458)   | Improve error reporting                                                                                                                                                          |
| 2.4.0   | 2024-01-24 | [34468](https://github.com/airbytehq/airbyte/pull/34468)   | Upgrade CDK to 0.14.0                                                                                                                                                            |
| 2.3.31  | 2024-01-22 | [\#34023](https://github.com/airbytehq/airbyte/pull/34023) | Combine DDL operations into a single execution                                                                                                                                   |
| 2.3.30  | 2024-01-12 | [\#34226](https://github.com/airbytehq/airbyte/pull/34226) | Upgrade CDK to 0.12.0; Cleanup dependencies                                                                                                                                      |
| 2.3.29  | 2024-01-09 | [\#34003](https://github.com/airbytehq/airbyte/pull/34003) | Fix loading credentials from GCP Env                                                                                                                                             |
| 2.3.28  | 2024-01-08 | [\#34021](https://github.com/airbytehq/airbyte/pull/34021) | Add idempotency ids in dummy insert for check call                                                                                                                               |
| 2.3.27  | 2024-01-05 | [\#33948](https://github.com/airbytehq/airbyte/pull/33948) | Skip retrieving initial table state when setup fails                                                                                                                             |
| 2.3.26  | 2024-01-04 | [\#33730](https://github.com/airbytehq/airbyte/pull/33730) | Internal code structure changes                                                                                                                                                  |
| 2.3.25  | 2023-12-20 | [\#33704](https://github.com/airbytehq/airbyte/pull/33704) | Update to java CDK 0.10.0 (no changes)                                                                                                                                           |
| 2.3.24  | 2023-12-20 | [\#33697](https://github.com/airbytehq/airbyte/pull/33697) | Stop creating unnecessary tmp tables                                                                                                                                             |
| 2.3.23  | 2023-12-18 | [\#33124](https://github.com/airbytehq/airbyte/pull/33124) | Make Schema Creation Separate from Table Creation                                                                                                                                |
| 2.3.22  | 2023-12-14 | [\#33451](https://github.com/airbytehq/airbyte/pull/33451) | Remove old spec option                                                                                                                                                           |
| 2.3.21  | 2023-12-13 | [\#33232](https://github.com/airbytehq/airbyte/pull/33232) | Only run typing+deduping for a stream if the stream had any records                                                                                                              |
| 2.3.20  | 2023-12-08 | [\#33263](https://github.com/airbytehq/airbyte/pull/33263) | Adopt java CDK version 0.7.0                                                                                                                                                     |
| 2.3.19  | 2023-12-07 | [\#32326](https://github.com/airbytehq/airbyte/pull/32326) | Update common T&D interfaces                                                                                                                                                     |
| 2.3.18  | 2023-12-04 | [\#33084](https://github.com/airbytehq/airbyte/pull/33084) | T&D SQL statements moved to debug log level                                                                                                                                      |
| 2.3.17  | 2023-12-04 | [\#33078](https://github.com/airbytehq/airbyte/pull/33078) | Further increase gcs COPY timeout                                                                                                                                                |
| 2.3.16  | 2023-11-14 | [\#32526](https://github.com/airbytehq/airbyte/pull/32526) | Clean up memory manager logs.                                                                                                                                                    |
| 2.3.15  | 2023-11-13 | [\#32468](https://github.com/airbytehq/airbyte/pull/32468) | Further error grouping enhancements                                                                                                                                              |
| 2.3.14  | 2023-11-06 | [\#32234](https://github.com/airbytehq/airbyte/pull/32234) | Remove unused config option.                                                                                                                                                     |
| 2.3.13  | 2023-11-08 | [\#32125](https://github.com/airbytehq/airbyte/pull/32125) | fix compiler warnings                                                                                                                                                            |
| 2.3.12  | 2023-11-08 | [\#32309](https://github.com/airbytehq/airbyte/pull/32309) | Revert: Use Typed object for connection config                                                                                                                                   |
| 2.3.11  | 2023-11-07 | [\#32147](https://github.com/airbytehq/airbyte/pull/32147) | Use Typed object for connection config                                                                                                                                           |
| 2.3.10  | 2023-11-07 | [\#32261](https://github.com/airbytehq/airbyte/pull/32261) | Further improve error reporting                                                                                                                                                  |
| 2.3.9   | 2023-11-07 | [\#32112](https://github.com/airbytehq/airbyte/pull/32112) | GCS staging mode: reduce flush frequency to use rate limit more efficiently                                                                                                      |
| 2.3.8   | 2023-11-06 | [\#32026](https://github.com/airbytehq/airbyte/pull/32026) | Move SAFE_CAST transaction to separate transactions                                                                                                                              |
| 2.3.7   | 2023-11-06 | [\#32190](https://github.com/airbytehq/airbyte/pull/32190) | Further improve error reporting                                                                                                                                                  |
| 2.3.6   | 2023-11-06 | [\#32193](https://github.com/airbytehq/airbyte/pull/32193) | Adopt java CDK version 0.4.1.                                                                                                                                                    |
| 2.3.5   | 2023-11-02 | [\#31983](https://github.com/airbytehq/airbyte/pull/31983) | Improve error reporting                                                                                                                                                          |
| 2.3.4   | 2023-10-31 | [\#32010](https://github.com/airbytehq/airbyte/pull/32010) | Add additional data centers.                                                                                                                                                     |
| 2.3.3   | 2023-10-30 | [\#31985](https://github.com/airbytehq/airbyte/pull/31985) | Delay upgrade deadline to Nov 7                                                                                                                                                  |
| 2.3.2   | 2023-10-30 | [\#31960](https://github.com/airbytehq/airbyte/pull/31960) | Adopt java CDK version 0.2.0.                                                                                                                                                    |
| 2.3.1   | 2023-10-27 | [\#31529](https://github.com/airbytehq/airbyte/pull/31529) | Performance enhancement (switch to a `merge` statement for incremental-dedup syncs)                                                                                              |
| 2.3.0   | 2023-10-25 | [\#31686](https://github.com/airbytehq/airbyte/pull/31686) | Opt out flag for typed and deduped tables                                                                                                                                        |
| 2.2.0   | 2023-10-25 | [\#31520](https://github.com/airbytehq/airbyte/pull/31520) | Stop deduping raw table                                                                                                                                                          |
| 2.1.6   | 2023-10-23 | [\#31717](https://github.com/airbytehq/airbyte/pull/31717) | Remove inadvertent Destination v2 check                                                                                                                                          |
| 2.1.5   | 2023-10-17 | [\#30069](https://github.com/airbytehq/airbyte/pull/30069) | Staging destination async                                                                                                                                                        |
| 2.1.4   | 2023-10-17 | [\#31191](https://github.com/airbytehq/airbyte/pull/31191) | Improve typing+deduping performance by filtering new raw records on extracted_at                                                                                                 |
| 2.1.3   | 2023-10-10 | [\#31358](https://github.com/airbytehq/airbyte/pull/31358) | Stringify array and object types for type:string column in final table                                                                                                           |
| 2.1.2   | 2023-10-10 | [\#31194](https://github.com/airbytehq/airbyte/pull/31194) | Deallocate unused per stream buffer memory when empty                                                                                                                            |
| 2.1.1   | 2023-10-10 | [\#31083](https://github.com/airbytehq/airbyte/pull/31083) | Fix precision of numeric values in async destinations                                                                                                                            |
| 2.1.0   | 2023-10-09 | [\#31149](https://github.com/airbytehq/airbyte/pull/31149) | No longer fail syncs when PKs are null - try do dedupe anyway                                                                                                                    |
| 2.0.26  | 2023-10-09 | [\#31198](https://github.com/airbytehq/airbyte/pull/31198) | Clarify configuration groups                                                                                                                                                     |
| 2.0.25  | 2023-10-09 | [\#31185](https://github.com/airbytehq/airbyte/pull/31185) | Increase staging file upload timeout to 5 minutes                                                                                                                                |
| 2.0.24  | 2023-10-06 | [\#31139](https://github.com/airbytehq/airbyte/pull/31139) | Bump CDK version                                                                                                                                                                 |
| 2.0.23  | 2023-10-06 | [\#31129](https://github.com/airbytehq/airbyte/pull/31129) | Reduce async buffer size                                                                                                                                                         |
| 2.0.22  | 2023-10-04 | [\#31082](https://github.com/airbytehq/airbyte/pull/31082) | Revert null PK checks                                                                                                                                                            |
| 2.0.21  | 2023-10-03 | [\#31028](https://github.com/airbytehq/airbyte/pull/31028) | Update timeout                                                                                                                                                                   |
| 2.0.20  | 2023-09-26 | [\#30779](https://github.com/airbytehq/airbyte/pull/30779) | Final table PK columns become non-null and skip check for null PKs in raw records (performance)                                                                                  |
| 2.0.19  | 2023-09-26 | [\#30775](https://github.com/airbytehq/airbyte/pull/30775) | Increase async block size                                                                                                                                                        |
| 2.0.18  | 2023-09-27 | [\#30739](https://github.com/airbytehq/airbyte/pull/30739) | Fix column name collision detection                                                                                                                                              |
| 2.0.17  | 2023-09-26 | [\#30696](https://github.com/airbytehq/airbyte/pull/30696) | Attempt unsafe typing operations with an exception clause                                                                                                                        |
| 2.0.16  | 2023-09-22 | [\#30697](https://github.com/airbytehq/airbyte/pull/30697) | Improve resiliency to unclean exit during schema change                                                                                                                          |
| 2.0.15  | 2023-09-21 | [\#30640](https://github.com/airbytehq/airbyte/pull/30640) | Handle streams with identical name and namespace                                                                                                                                 |
| 2.0.14  | 2023-09-20 | [\#30069](https://github.com/airbytehq/airbyte/pull/30069) | Staging destination async                                                                                                                                                        |
| 2.0.13  | 2023-09-19 | [\#30592](https://github.com/airbytehq/airbyte/pull/30592) | Internal code changes                                                                                                                                                            |
| 2.0.12  | 2023-09-19 | [\#30319](https://github.com/airbytehq/airbyte/pull/30319) | Improved testing                                                                                                                                                                 |
| 2.0.11  | 2023-09-18 | [\#30551](https://github.com/airbytehq/airbyte/pull/30551) | GCS Staging is first loading method option                                                                                                                                       |
| 2.0.10  | 2023-09-15 | [\#30491](https://github.com/airbytehq/airbyte/pull/30491) | Improve error message display                                                                                                                                                    |
| 2.0.9   | 2023-09-14 | [\#30439](https://github.com/airbytehq/airbyte/pull/30439) | Fix a transient error                                                                                                                                                            |
| 2.0.8   | 2023-09-12 | [\#30364](https://github.com/airbytehq/airbyte/pull/30364) | Add log message                                                                                                                                                                  |
| 2.0.7   | 2023-08-29 | [\#29878](https://github.com/airbytehq/airbyte/pull/29878) | Internal code changes                                                                                                                                                            |
| 2.0.6   | 2023-09-05 | [\#29917](https://github.com/airbytehq/airbyte/pull/29917) | Improve performance by changing metadata error array construction from ARRAY_CONCAT to ARRAY_AGG                                                                                 |
| 2.0.5   | 2023-08-31 | [\#30020](https://github.com/airbytehq/airbyte/pull/30020) | Run typing and deduping tasks in parallel                                                                                                                                        |
| 2.0.4   | 2023-09-05 | [\#30117](https://github.com/airbytehq/airbyte/pull/30117) | Type and Dedupe at sync start and then every 6 hours                                                                                                                             |
| 2.0.3   | 2023-09-01 | [\#30056](https://github.com/airbytehq/airbyte/pull/30056) | Internal refactor, no behavior change                                                                                                                                            |
| 2.0.2   | 2023-09-01 | [\#30120](https://github.com/airbytehq/airbyte/pull/30120) | Improve performance on very wide streams by skipping SAFE_CAST on strings                                                                                                        |
| 2.0.1   | 2023-08-29 | [\#29972](https://github.com/airbytehq/airbyte/pull/29972) | Publish a new version to supersede old v2.0.0                                                                                                                                    |
| 2.0.0   | 2023-08-27 | [\#29783](https://github.com/airbytehq/airbyte/pull/29783) | Destinations V2                                                                                                                                                                  |
| 1.10.2  | 2023-08-24 | [\#29805](https://github.com/airbytehq/airbyte/pull/29805) | Destinations v2: Don't soft reset in migration                                                                                                                                   |
| 1.10.1  | 2023-08-23 | [\#29774](https://github.com/airbytehq/airbyte/pull/29774) | Destinations v2: Don't soft reset overwrite syncs                                                                                                                                |
| 1.10.0  | 2023-08-21 | [\#29636](https://github.com/airbytehq/airbyte/pull/29636) | Destinations v2: Several Critical Bug Fixes (cursorless dedup, improved floating-point handling, improved special characters handling; improved error handling)                  |
| 1.9.1   | 2023-08-21 | [\#28687](https://github.com/airbytehq/airbyte/pull/28687) | Under the hood: Add dependency on Java CDK v0.0.1.                                                                                                                               |
| 1.9.0   | 2023-08-17 | [\#29560](https://github.com/airbytehq/airbyte/pull/29560) | Destinations v2: throw an error on disallowed column name prefixes                                                                                                               |
| 1.8.1   | 2023-08-17 | [\#29522](https://github.com/airbytehq/airbyte/pull/29522) | Migration BugFix - ensure raw dataset created                                                                                                                                    |
| 1.8.0   | 2023-08-17 | [\#29498](https://github.com/airbytehq/airbyte/pull/29498) | Fix checkpointing logic in GCS staging mode                                                                                                                                      |
| 1.7.8   | 2023-08-15 | [\#29461](https://github.com/airbytehq/airbyte/pull/29461) | Migration BugFix - ensure migration happens before table creation for GCS staging.                                                                                               |
| 1.7.7   | 2023-08-11 | [\#29381](https://github.com/airbytehq/airbyte/pull/29381) | Destinations v2: Add support for streams with no columns                                                                                                                         |
| 1.7.6   | 2023-08-04 | [\#28894](https://github.com/airbytehq/airbyte/pull/28894) | Destinations v2: Add v1 -> v2 migration Logic                                                                                                                                    |
| 1.7.5   | 2023-08-04 | [\#29106](https://github.com/airbytehq/airbyte/pull/29106) | Destinations v2: handle unusual CDC deletion edge case                                                                                                                           |
| 1.7.4   | 2023-08-04 | [\#29089](https://github.com/airbytehq/airbyte/pull/29089) | Destinations v2: improve special character handling in column names                                                                                                              |
| 1.7.3   | 2023-08-03 | [\#28890](https://github.com/airbytehq/airbyte/pull/28890) | Internal code updates; improved testing                                                                                                                                          |
| 1.7.2   | 2023-08-02 | [\#28976](https://github.com/airbytehq/airbyte/pull/28976) | Fix composite PK handling in v1 mode                                                                                                                                             |
| 1.7.1   | 2023-08-02 | [\#28959](https://github.com/airbytehq/airbyte/pull/28959) | Destinations v2: Fix CDC syncs in non-dedup mode                                                                                                                                 |
| 1.7.0   | 2023-08-01 | [\#28894](https://github.com/airbytehq/airbyte/pull/28894) | Destinations v2: Open up early access program opt-in                                                                                                                             |
| 1.6.0   | 2023-07-26 | [\#28723](https://github.com/airbytehq/airbyte/pull/28723) | Destinations v2: Change raw table dataset and naming convention                                                                                                                  |
| 1.5.8   | 2023-07-25 | [\#28721](https://github.com/airbytehq/airbyte/pull/28721) | Destinations v2: Handle cursor change across syncs                                                                                                                               |
| 1.5.7   | 2023-07-24 | [\#28625](https://github.com/airbytehq/airbyte/pull/28625) | Destinations v2: Limit Clustering Columns to 4                                                                                                                                   |
| 1.5.6   | 2023-07-21 | [\#28580](https://github.com/airbytehq/airbyte/pull/28580) | Destinations v2: Create dataset in user-specified location                                                                                                                       |
| 1.5.5   | 2023-07-20 | [\#28490](https://github.com/airbytehq/airbyte/pull/28490) | Destinations v2: Fix schema change detection in OVERWRITE mode when existing table is empty; other code refactoring                                                              |
| 1.5.4   | 2023-07-17 | [\#28382](https://github.com/airbytehq/airbyte/pull/28382) | Destinations v2: Schema Change Detection                                                                                                                                         |
| 1.5.3   | 2023-07-14 | [\#28345](https://github.com/airbytehq/airbyte/pull/28345) | Increment patch to trigger a rebuild                                                                                                                                             |
| 1.5.2   | 2023-07-05 | [\#27936](https://github.com/airbytehq/airbyte/pull/27936) | Internal scaffolding change for future development                                                                                                                               |
| 1.5.1   | 2023-06-30 | [\#27891](https://github.com/airbytehq/airbyte/pull/27891) | Revert bugged update                                                                                                                                                             |
| 1.5.0   | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                                                                                             |
| 1.4.6   | 2023-06-28 | [\#27268](https://github.com/airbytehq/airbyte/pull/27268) | Internal scaffolding change for future development                                                                                                                               |
| 1.4.5   | 2023-06-21 | [\#27555](https://github.com/airbytehq/airbyte/pull/27555) | Reduce image size                                                                                                                                                                |
| 1.4.4   | 2023-05-25 | [\#26585](https://github.com/airbytehq/airbyte/pull/26585) | Small tweak in logs for clarity                                                                                                                                                  |
| 1.4.3   | 2023-05-17 | [\#26213](https://github.com/airbytehq/airbyte/pull/26213) | Fix bug in parsing file buffer config count                                                                                                                                      |
| 1.4.2   | 2023-05-10 | [\#25925](https://github.com/airbytehq/airbyte/pull/25925) | Testing update. Normalization tests are now done in the destination container.                                                                                                   |
| 1.4.1   | 2023-05-11 | [\#25993](https://github.com/airbytehq/airbyte/pull/25993) | Internal library update                                                                                                                                                          |
| 1.4.0   | 2023-04-29 | [\#25570](https://github.com/airbytehq/airbyte/pull/25570) | Internal library update. Bumping version to stay in sync with BigQuery-denormalized.                                                                                             |
| 1.3.4   | 2023-04-28 | [\#25588](https://github.com/airbytehq/airbyte/pull/25588) | Internal scaffolding change for future development                                                                                                                               |
| 1.3.3   | 2023-04-27 | [\#25346](https://github.com/airbytehq/airbyte/pull/25346) | Internal code cleanup                                                                                                                                                            |
| 1.3.1   | 2023-04-20 | [\#25097](https://github.com/airbytehq/airbyte/pull/25097) | Internal scaffolding change for future development                                                                                                                               |
| 1.3.0   | 2023-04-19 | [\#25287](https://github.com/airbytehq/airbyte/pull/25287) | Add parameter to configure the number of file buffers when GCS is used as the loading method                                                                                     |
| 1.2.20  | 2023-04-12 | [\#25122](https://github.com/airbytehq/airbyte/pull/25122) | Add additional data centers                                                                                                                                                      |
| 1.2.19  | 2023-03-29 | [\#24671](https://github.com/airbytehq/airbyte/pull/24671) | Fail faster in certain error cases                                                                                                                                               |
| 1.2.18  | 2023-03-23 | [\#24447](https://github.com/airbytehq/airbyte/pull/24447) | Set the Service Account Key JSON field to always_show: true so that it isn't collapsed into an optional fields section                                                           |
| 1.2.17  | 2023-03-17 | [\#23788](https://github.com/airbytehq/airbyte/pull/23788) | S3-Parquet: added handler to process null values in arrays                                                                                                                       |
| 1.2.16  | 2023-03-10 | [\#23931](https://github.com/airbytehq/airbyte/pull/23931) | Added support for periodic buffer flush                                                                                                                                          |
| 1.2.15  | 2023-03-10 | [\#23466](https://github.com/airbytehq/airbyte/pull/23466) | Changed S3 Avro type from Int to Long                                                                                                                                            |
| 1.2.14  | 2023-02-08 | [\#22497](https://github.com/airbytehq/airbyte/pull/22497) | Fixed table already exists error                                                                                                                                                 |
| 1.2.13  | 2023-01-26 | [\#20631](https://github.com/airbytehq/airbyte/pull/20631) | Added support for destination checkpointing with staging                                                                                                                         |
| 1.2.12  | 2023-01-18 | [\#21087](https://github.com/airbytehq/airbyte/pull/21087) | Wrap Authentication Errors as Config Exceptions                                                                                                                                  |
| 1.2.11  | 2023-01-18 | [\#21144](https://github.com/airbytehq/airbyte/pull/21144) | Added explicit error message if sync fails due to a config issue                                                                                                                 |
| 1.2.9   | 2022-12-14 | [\#20501](https://github.com/airbytehq/airbyte/pull/20501) | Report GCS staging failures that occur during connection check                                                                                                                   |
| 1.2.8   | 2022-11-22 | [\#19489](https://github.com/airbytehq/airbyte/pull/19489) | Added non-billable projects handle to check connection stage                                                                                                                     |
| 1.2.7   | 2022-11-11 | [\#19358](https://github.com/airbytehq/airbyte/pull/19358) | Fixed check method to capture mismatch dataset location                                                                                                                          |
| 1.2.6   | 2022-11-10 | [\#18554](https://github.com/airbytehq/airbyte/pull/18554) | Improve check connection method to handle more errors                                                                                                                            |
| 1.2.5   | 2022-10-19 | [\#18162](https://github.com/airbytehq/airbyte/pull/18162) | Improve error logs                                                                                                                                                               |
| 1.2.4   | 2022-09-26 | [\#16890](https://github.com/airbytehq/airbyte/pull/16890) | Add user-agent header                                                                                                                                                            |
| 1.2.3   | 2022-09-22 | [\#17054](https://github.com/airbytehq/airbyte/pull/17054) | Respect stream namespace                                                                                                                                                         |
| 1.2.1   | 2022-09-14 | [\#15668](https://github.com/airbytehq/airbyte/pull/15668) | (bugged, do not use) Wrap logs in AirbyteLogMessage                                                                                                                              |
| 1.2.0   | 2022-09-09 | [\#14023](https://github.com/airbytehq/airbyte/pull/14023) | (bugged, do not use) Cover arrays only if they are nested                                                                                                                        |
| 1.1.16  | 2022-09-01 | [\#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields)                                                         |
| 1.1.15  | 2022-08-22 | [\#15787](https://github.com/airbytehq/airbyte/pull/15787) | Throw exception if job failed                                                                                                                                                    |
| 1.1.14  | 2022-08-03 | [\#14784](https://github.com/airbytehq/airbyte/pull/14784) | Enabling Application Default Credentials                                                                                                                                         |
| 1.1.13  | 2022-08-02 | [\#14801](https://github.com/airbytehq/airbyte/pull/14801) | Fix multiple log bindings                                                                                                                                                        |
| 1.1.12  | 2022-08-02 | [\#15180](https://github.com/airbytehq/airbyte/pull/15180) | Fix standard loading mode                                                                                                                                                        |
| 1.1.11  | 2022-06-24 | [\#14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                                                                                      |
| 1.1.10  | 2022-06-16 | [\#13852](https://github.com/airbytehq/airbyte/pull/13852) | Updated stacktrace format for any trace message errors                                                                                                                           |
| 1.1.9   | 2022-06-17 | [\#13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                                                                          |
| 1.1.8   | 2022-06-07 | [\#13579](https://github.com/airbytehq/airbyte/pull/13579) | Always check GCS bucket for GCS loading method to catch invalid HMAC keys.                                                                                                       |
| 1.1.7   | 2022-06-07 | [\#13424](https://github.com/airbytehq/airbyte/pull/13424) | Reordered fields for specification.                                                                                                                                              |
| 1.1.6   | 2022-05-15 | [\#12768](https://github.com/airbytehq/airbyte/pull/12768) | Clarify that the service account key json field is required on cloud.                                                                                                            |
| 1.1.5   | 2022-05-12 | [\#12805](https://github.com/airbytehq/airbyte/pull/12805) | Updated to latest base-java to emit AirbyteTraceMessage on error.                                                                                                                |
| 1.1.4   | 2022-05-04 | [\#12578](https://github.com/airbytehq/airbyte/pull/12578) | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                                                                                  |
| 1.1.3   | 2022-05-02 | [\#12528](https://github.com/airbytehq/airbyte/pull/12528) | Update Dataset location field description                                                                                                                                        |
| 1.1.2   | 2022-04-29 | [\#12477](https://github.com/airbytehq/airbyte/pull/12477) | Dataset location is a required field                                                                                                                                             |
| 1.1.1   | 2022-04-15 | [\#12068](https://github.com/airbytehq/airbyte/pull/12068) | Fixed bug with GCS bucket conditional binding                                                                                                                                    |
| 1.1.0   | 2022-04-06 | [\#11776](https://github.com/airbytehq/airbyte/pull/11776) | Use serialized buffering strategy to reduce memory consumption.                                                                                                                  |
| 1.0.2   | 2022-03-30 | [\#11620](https://github.com/airbytehq/airbyte/pull/11620) | Updated spec                                                                                                                                                                     |
| 1.0.1   | 2022-03-24 | [\#11350](https://github.com/airbytehq/airbyte/pull/11350) | Improve check performance                                                                                                                                                        |
| 1.0.0   | 2022-03-18 | [\#11238](https://github.com/airbytehq/airbyte/pull/11238) | Updated spec and documentation                                                                                                                                                   |
| 0.6.12  | 2022-03-18 | [\#10793](https://github.com/airbytehq/airbyte/pull/10793) | Fix namespace with invalid characters                                                                                                                                            |
| 0.6.11  | 2022-03-03 | [\#10755](https://github.com/airbytehq/airbyte/pull/10755) | Make sure to kill children threads and stop JVM                                                                                                                                  |
| 0.6.8   | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                                                                                     |
| 0.6.6   | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959)   | Fix null pointer exception from buffered stream consumer.                                                                                                                        |
| 0.6.6   | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745)   | Integrate with Sentry.                                                                                                                                                           |
| 0.6.5   | 2022-01-18 | [\#9573](https://github.com/airbytehq/airbyte/pull/9573)   | BigQuery Destination : update description for some input fields                                                                                                                  |
| 0.6.4   | 2022-01-17 | [\#8383](https://github.com/airbytehq/airbyte/issues/8383) | Support dataset-id prefixed by project-id                                                                                                                                        |
| 0.6.3   | 2022-01-12 | [\#9415](https://github.com/airbytehq/airbyte/pull/9415)   | BigQuery Destination : Fix GCS processing of Facebook data                                                                                                                       |
| 0.6.2   | 2022-01-10 | [\#9121](https://github.com/airbytehq/airbyte/pull/9121)   | Fixed check method for GCS mode to verify if all roles assigned to user                                                                                                          |
| 0.6.1   | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration to UI for GCS staging                                                                                                                              |
| 0.6.0   | 2021-12-17 | [\#8788](https://github.com/airbytehq/airbyte/issues/8788) | BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files                                                                                      |
| 0.5.1   | 2021-12-16 | [\#8816](https://github.com/airbytehq/airbyte/issues/8816) | Update dataset locations                                                                                                                                                         |
| 0.5.0   | 2021-10-26 | [\#7240](https://github.com/airbytehq/airbyte/issues/7240) | Output partitioned/clustered tables                                                                                                                                              |
| 0.4.1   | 2021-10-04 | [\#6733](https://github.com/airbytehq/airbyte/issues/6733) | Support dataset starting with numbers                                                                                                                                            |
| 0.4.0   | 2021-08-26 | [\#5296](https://github.com/airbytehq/airbyte/issues/5296) | Added GCS Staging uploading option                                                                                                                                               |
| 0.3.12  | 2021-08-03 | [\#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add optional arg to make a possibility to change the BigQuery client's chunk\buffer size                                                                                         |
| 0.3.11  | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                                                                                                     |
| 0.3.10  | 2021-07-28 | [\#3549](https://github.com/airbytehq/airbyte/issues/3549) | Add extended logs and made JobId filled with region and projectId                                                                                                                |
| 0.3.9   | 2021-07-28 | [\#5026](https://github.com/airbytehq/airbyte/pull/5026)   | Add sanitized json fields in raw tables to handle quotes in column names                                                                                                         |
| 0.3.6   | 2021-06-18 | [\#3947](https://github.com/airbytehq/airbyte/issues/3947) | Service account credentials are now optional.                                                                                                                                    |
| 0.3.4   | 2021-06-07 | [\#3277](https://github.com/airbytehq/airbyte/issues/3277) | Add dataset location option                                                                                                                                                      |

</details>
