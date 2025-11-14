# GCS Data Lake

This page guides you through setting up the GCS Data Lake destination connector.

This connector is Airbyte's official support for the Iceberg protocol on Google Cloud Storage. It writes the Iceberg table format to GCS using a supported Iceberg catalog.

## Prerequisites

The GCS Data Lake connector requires two things:

1. A Google Cloud Storage bucket
2. A supported Iceberg catalog. Currently, the connector supports these catalogs:
   - BigLake
   - Polaris

## Setup guide

Follow these steps to set up your GCS storage and Iceberg catalog permissions.

### GCS setup and permissions

#### Create a GCS bucket

1. Open the [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Cloud Storage** > **Buckets**
3. Click **CREATE BUCKET**
4. Choose a bucket name and location
5. Select a storage class and access control settings
6. Click **CREATE**

#### Create a service account

1. In the Google Cloud Console, navigate to **IAM & Admin** > **Service Accounts**
2. Click **CREATE SERVICE ACCOUNT**
3. Give it a name (for example: `airbyte-gcs-data-lake`)
4. Grant the following roles:
   - **Storage Admin** - For full GCS bucket access
   - **BigQuery Data Editor** - For BigLake catalog operations
   - **BigQuery User** - For BigQuery operations
   - **Service Usage Consumer** - For using GCP services

5. Click **CREATE KEY** and choose the **JSON** format
6. Download the JSON key file
7. In Airbyte, paste the entire contents of this JSON file into the **Service Account JSON** field

### Iceberg catalog setup and permissions

The rest of the setup process differs depending on the catalog you're using.

#### BigLake

The BigLake catalog is Google Cloud's managed Iceberg catalog service. To use BigLake, you need to have created a BigLake catalog in your GCP project. The service account you created earlier should have the necessary permissions to access this catalog.

#### Polaris

To authenticate with Apache Polaris, follow these steps:

1. Set up your Polaris catalog and create a principal with the necessary permissions. Refer to the [Apache Polaris documentation](https://polaris.apache.org/) for detailed setup instructions.

2. When creating a principal in Polaris, you'll receive OAuth credentials (Client ID and Client Secret). Keep these credentials secure.

3. Grant the required privileges to your principal's catalog role. You can either:

   **Option A: grant the broad `CATALOG_MANAGE_CONTENT` privilege** (recommended for simplicity):
    - This single privilege allows the connector to manage tables and namespaces in the catalog

   **Option B: grant specific granular privileges**:
    - `TABLE_LIST` - List tables in a namespace
    - `TABLE_CREATE` - Create new tables
    - `TABLE_DROP` - Delete tables
    - `TABLE_READ_PROPERTIES` - Read table metadata
    - `TABLE_WRITE_PROPERTIES` - Update table metadata
    - `TABLE_WRITE_DATA` - Write data to tables
    - `NAMESPACE_LIST` - List namespaces
    - `NAMESPACE_CREATE` - Create new namespaces
    - `NAMESPACE_READ_PROPERTIES` - Read namespace metadata

4. Ensure that your Polaris catalog has been configured with the appropriate storage credentials to access your GCS bucket.

## Configuration

In Airbyte, configure the following fields:

### Common fields (all catalog types)

| Field                    | Required   | Description                                                                  |
|--------------------------|------------|------------------------------------------------------------------------------|
| **GCS Bucket Name**      | Yes        | The name of your GCS bucket (for example: `my-data-lake`)                    |
| **Service Account JSON** | Yes        | The complete JSON content from your service account key file                 |
| **GCP Project ID**       | No         | The GCP project ID. If not specified, extracted from service account         |
| **GCP Location**         | Yes        | The GCP location/region (for example: `us`, `us-central1`, `eu`)             |
| **Warehouse Location**   | Yes        | Root path for Iceberg data in GCS (for example: `gs://my-bucket/warehouse`)  |
| **Catalog Type**         | Yes        | Select the type of Iceberg catalog to use: `BigLake` or `Polaris`            |
| **Main Branch Name**     | No         | Iceberg branch name (default: `main`)                                        |

### BigLake-specific fields

When **Catalog Type** is set to `BigLake`, configure these additional fields:

| Field                    | Required   | Description                                                          |
|--------------------------|------------|----------------------------------------------------------------------|
| **BigLake Catalog Name** | Yes        | Name of your BigLake catalog (from the setup step)                   |
| **BigLake Database**     | Yes        | Default database/namespace for tables                                |

### Polaris-specific fields

When **Catalog Type** is set to `Polaris`, configure these additional fields:

| Field                  | Required   | Description                                                                            |
|------------------------|------------|----------------------------------------------------------------------------------------|
| **Polaris Server URI** | Yes        | The base URL of your Polaris server (for example: `http://localhost:8181/api/catalog`) |
| **Catalog Name**       | Yes        | The name of the catalog in Polaris (for example: `quickstart_catalog`)                 |
| **Client ID**          | Yes        | The OAuth Client ID for authenticating with the Polaris server                         |
| **Client Secret**      | Yes        | The OAuth Client Secret for authenticating with the Polaris server                     |

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

At the end of stream sync, the current `main` branch is replaced with the `airbyte_staging` branch. Fast-forwarding is intentionally avoided to better handle potential compaction issues.

**Important Warning**: any changes made to the `main` branch outside of Airbyte's operations after a sync begins is going to be lost during this process.

## Compaction

:::caution
**Do not run compaction during a truncate refresh sync to prevent data loss.**
During a truncate refresh sync, the system deletes all files that don't belong to the latest generation. This includes:

- Files without generation IDs (compacted files)
- Files from previous generations

If compaction runs simultaneously with the sync, it would delete files from the current generation, causing data loss.
:::

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                 | Subject                                                                               |
|:--------|:-----------|:-------------------------------------------------------------|:--------------------------------------------------------------------------------------|
| 1.0.2   | 2025-11-13 | [69317](https://github.com/airbytehq/airbyte/pull/69317)     | Connector generally available                                                         |
| 1.0.1   | 2025-11-13 | [69212](https://github.com/airbytehq/airbyte/pull/69212)     | Initial release of GCS Data Lake destination with BigLake and Polaris catalog support |

</details>
