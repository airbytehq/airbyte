# GCS Data Lake

This page guides you through setting up the GCS Data Lake destination connector.

This connector is Airbyte's official support for the Iceberg protocol on Google Cloud Storage. It writes the Iceberg table format to GCS using the BigLake catalog.

## Prerequisites

The GCS Data Lake connector requires two things:

1. A Google Cloud Storage bucket
2. A BigLake Iceberg catalog

## Setup guide

Follow these steps to set up your GCS storage and BigLake catalog permissions.

### GCS setup and permissions

#### Create a GCS bucket

1. Open the [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Cloud Storage** > **Buckets**
3. Click **CREATE BUCKET**
4. Choose a bucket name and location
5. Select storage class and access control settings
6. Click **CREATE**

#### Create a service account

1. In the Google Cloud Console, navigate to **IAM & Admin** > **Service Accounts**
2. Click **CREATE SERVICE ACCOUNT**
3. Give it a name (e.g., `airbyte-gcs-data-lake`)
4. Grant the following roles:
   - **Storage Admin** - For full GCS bucket access
   - **BigQuery Data Editor** - For BigLake catalog operations
   - **BigQuery User** - For BigQuery operations
   - **Service Usage Consumer** - For using GCP services

5. Click **CREATE KEY** > Choose **JSON** format
6. Download the JSON key file
7. In Airbyte, paste the entire contents of this JSON file into the **Service Account JSON** field

## Configuration

In Airbyte, configure the following fields:

| Field | Required | Description |
|-------|----------|-------------|
| **GCS Bucket Name** | Yes | The name of your GCS bucket (e.g., `my-data-lake`) |
| **Service Account JSON** | Yes | The complete JSON content from your service account key file |
| **GCP Project ID** | No | The GCP project ID. If not specified, extracted from service account |
| **GCP Location** | Yes | The GCP location/region (e.g., `us`, `us-central1`, `eu`) |
| **Warehouse Location** | Yes | Root path for Iceberg data in GCS (e.g., `gs://my-bucket/warehouse`) |
| **BigLake Catalog Name** | Yes | Name of your BigLake catalog (from the setup step) |
| **BigLake Database** | Yes | Default database/namespace for tables |
| **Main Branch Name** | No | Iceberg branch name (default: `main`) |

## Output schema

### How Airbyte generates the Iceberg schema

In each stream, Airbyte maps top-level fields to Iceberg fields. Airbyte maps nested fields (objects, arrays, and unions) to string columns and writes them as serialized JSON.

This is the full mapping between Airbyte types and Iceberg types.

| Airbyte type               | Iceberg type                   |
|----------------------------|--------------------------------|
| Boolean                    | Boolean                        |
| Date                       | Date                           |
| Integer                    | Long                           |
| Number                     | Double                         |
| String                     | String                         |
| Time with timezone*        | Time                           |
| Time without timezone      | Time                           |
| Timestamp with timezone*   | Timestamp with timezone        |
| Timestamp without timezone | Timestamp without timezone     |
| Object                     | String (JSON-serialized value) |
| Array                      | String (JSON-serialized value) |
| Union                      | String (JSON-serialized value) |

*Airbyte converts the `time with timezone` and `timestamp with timezone` types to Coordinated Universal Time (UTC) before writing to the Iceberg file.

### Managing schema evolution

This connector never rewrites existing Iceberg data files. This means Airbyte can only handle specific source schema changes:

- Adding or removing a column
- Widening a column
- Changing the primary key

You have the following options to manage schema evolution:

- To handle unsupported schema changes automatically, use [Full Refresh - Overwrite](../../platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) as your [sync mode](../../platform/using-airbyte/core-concepts/sync-modes).
- To handle unsupported schema changes as they occur, wait for a sync to fail, then take action to restore it. Either:
    - Manually edit your table schema in Iceberg directly.
    - [Refresh](../../platform/operator-guides/refreshes) your connection in Airbyte.
    - [Clear](../../platform/operator-guides/clear) your connection in Airbyte.

## Deduplication

This connector uses a merge-on-read strategy to support deduplication.

- Airbyte translates the stream's primary keys to Iceberg's [identifier columns](https://iceberg.apache.org/spec/#identifier-field-ids).
- An "upsert" is an [equality-based delete](https://iceberg.apache.org/spec/#equality-delete-files) on that row's primary key, followed by an insertion of the new data.

### Assumptions about primary keys

The GCS Data Lake connector assumes that one of two things is true:

- The source never emits the same primary key twice in a single sync attempt.
- If the source emits the same primary key multiple times in a single attempt, it always emits those records in cursor order from oldest to newest.

If these conditions aren't met, you may see inaccurate data in Iceberg in the form of older records taking precedence over newer records. If this happens, use append or overwrite as your [sync modes](../../platform/using-airbyte/core-concepts/sync-modes/).

An unknown number of API sources have streams that don't meet these conditions. Airbyte knows [Stripe](../sources/stripe) and [Monday](../sources/monday) don't, but there are probably others.

## Branching and data availability

Iceberg supports [Git-like semantics](https://iceberg.apache.org/docs/latest/branching/) over your data. This connector leverages those semantics to provide resilient syncs.

- In each sync, each microbatch creates a new snapshot.
- During truncate syncs, the connector writes the refreshed data to the `airbyte_staging` branch and replaces the `main` branch with the `airbyte_staging` at the end of the sync. Since most query engines target the `main` branch, people can query your data until the end of a truncate sync, at which point it's atomically swapped to the new version.

### Branch replacement

At the end of stream sync, we replace the current `main` branch with the `airbyte_staging` branch we were working on. We intentionally avoid fast-forwarding to better handle potential compaction issues.

**Important Warning**: Any changes made to the `main` branch outside of Airbyte's operations after a sync begins will be lost during this process.

## Compaction

:::caution
**Do not run compaction during a truncate refresh sync to prevent data loss.**
During a truncate refresh sync, the system deletes all files that don't belong to the latest generation. This includes:

- Files without generation IDs (compacted files)
- Files from previous generations

If compaction runs simultaneously with the sync, it will delete files from the current generation, causing data loss. The system identifies generations by parsing file names for generation IDs.
:::

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                                                                         |
|:--------|:-----------|:-----------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------|
| 0.0.1   | 2025-10-30 | [69080](https://github.com/airbytehq/airbyte/pull/69080)  | Initial release of GCS Data Lake destination with BigLake catalog support                                                       |

</details>
