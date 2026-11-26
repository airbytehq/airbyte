# Firebolt

This page guides you through the process of setting up the Firebolt destination connector.

## Prerequisites

1. Firebolt Account: You need an active Firebolt account. Sign up [here](https://www.firebolt.io/) if you don’t have one.
2. Firebolt Database and Engine created: Follow the [guide](https://docs.firebolt.io/guides/operate-engines/working-with-engines-using-ddl) to create an engine if you don't have one in your Firebolt workspace.
3. Service Account credentials: all programmatic access to Firebolt requires a service account to interact with the database. Create a service account as described in this [guide](https://docs.firebolt.io/guides/managing-your-organization/service-accounts) and note its ID and secret.

## Replication strategy

The Firebolt destination is built on Airbyte's Java/Kotlin bulk-connector framework (DirectLoad).
Records are buffered into gzipped CSV files, uploaded to an S3 staging bucket, and loaded into the
target table with Firebolt's [COPY FROM](https://docs.firebolt.io/godocs/Guides/loading-data/loading-data.html).
Deduped syncs merge staged rows into the final table.

An S3 bucket and credentials are **required** in addition to Firebolt credentials.

## Connection parameters

- **Client ID**
  - Your service account id.
- **Client Secret**
  - Your service account secret.
- **Account**
  - Your firebolt [account](https://docs.firebolt.io/guides/managing-your-organization/managing-accounts).
- **Database**
  - The database name where you want the data to be stored.
- **Engine**
  - Name of the engine that will run the queries.
- **Host (optional)**
  - Firebolt backend URL. Can be left blank for most usecases.
- **Default Schema (optional)**
  - The Firebolt schema streams are written to when a stream has no namespace.
- **JDBC URL Params (optional)**
  - Additional parameters appended to the Firebolt JDBC connection URL.

### S3 staging configuration (required)

- **S3 Bucket Name**
  - See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to
    create an S3 bucket.
- **S3 Bucket Path (optional)**
  - Directory under the bucket where staging files are written. Defaults to the bucket root.
- **S3 Bucket Region**
  - Create the S3 bucket on the same region as the Firebolt database.
- **Access Key Id**
  - See
    [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
    on how to generate an access key.
  - We recommend creating an Airbyte-specific user. This user will require
    [read, write and delete permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)
    to objects in the staging bucket.
- **Secret Access Key**
  - Corresponding key to the above key id.
- **S3 Filename Pattern (optional)**
  - Pattern for naming staging files.
- **Purge Staging Files and Tables**
  - When enabled (default), staging files are deleted from S3 after the sync completes.

## Setup guide

1. Sign up to Firebolt following the
   [guide](https://docs.firebolt.io/godocs/Guides/managing-your-organization/creating-an-organization.html)
1. Follow the getting started [tutorial](https://docs.firebolt.io/godocs/Guides/getting-started.html) to setup a database.
1. Create a [service account](https://docs.firebolt.io/godocs/Guides/managing-your-organization/service-accounts.html).
1. Create an engine as described in
   [here](https://docs.firebolt.io/godocs/Guides/working-with-engines/working-with-engines-using-the-firebolt-manager.html)
1. [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) a
   staging S3 bucket.
1. [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-iam-policies.html) an IAM
   with programmatic access to read, write and delete objects from an S3 bucket.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | Yes |

## Connector-specific features & highlights

### Output schema

Each stream is written to its own final
[table](https://docs.firebolt.io/working-with-tables.html#fact-and-dimension-tables) in Firebolt.
The table contains one typed column per stream field (mapped from the stream's JSON schema to
Firebolt types) plus the Airbyte metadata columns:

- `_airbyte_raw_id`: a unique identifier assigned to each record by Airbyte.
- `_airbyte_extracted_at`: a timestamp representing when the record was pulled from the source.
- `_airbyte_meta`: metadata about the record, including change tracking and sync errors.
- `_airbyte_generation_id`: a monotonically increasing identifier used to track refreshes.

## Namespace support

Stream [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces) map to
Firebolt schemas, which the connector creates automatically on first sync. Streams without a
namespace are written to the configured Default Schema.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                |
|:--------| :--------- | :------------------------------------------------------- | :------------------------------------- |
| 0.3.0 | 2026-08-29 | [85191](https://github.com/airbytehq/airbyte/pull/85191) | Rewrite as V2 Java/Kotlin DirectLoad connector with S3 staging and SQL generator |
| 0.2.41 | 2026-10-07 | [88246](https://github.com/airbytehq/airbyte/pull/88246) | Add missing `destination_firebolt.run` entrypoint module so the connector image starts with the shared python-connector Dockerfile |
| 0.2.40 | 2025-05-24 | [59866](https://github.com/airbytehq/airbyte/pull/59866) | Update dependencies |
| 0.2.39 | 2025-05-03 | [59316](https://github.com/airbytehq/airbyte/pull/59316) | Update dependencies |
| 0.2.38 | 2025-04-26 | [58725](https://github.com/airbytehq/airbyte/pull/58725) | Update dependencies |
| 0.2.37 | 2025-04-19 | [57623](https://github.com/airbytehq/airbyte/pull/57623) | Update dependencies |
| 0.2.36 | 2025-04-05 | [57115](https://github.com/airbytehq/airbyte/pull/57115) | Update dependencies |
| 0.2.35 | 2025-03-29 | [56607](https://github.com/airbytehq/airbyte/pull/56607) | Update dependencies |
| 0.2.34 | 2025-03-22 | [56156](https://github.com/airbytehq/airbyte/pull/56156) | Update dependencies |
| 0.2.33 | 2025-03-08 | [55391](https://github.com/airbytehq/airbyte/pull/55391) | Update dependencies |
| 0.2.32 | 2025-03-01 | [54853](https://github.com/airbytehq/airbyte/pull/54853) | Update dependencies |
| 0.2.31 | 2025-02-22 | [54217](https://github.com/airbytehq/airbyte/pull/54217) | Update dependencies |
| 0.2.30 | 2025-02-15 | [53940](https://github.com/airbytehq/airbyte/pull/53940) | Update dependencies |
| 0.2.29 | 2025-02-08 | [53427](https://github.com/airbytehq/airbyte/pull/53427) | Update dependencies |
| 0.2.28 | 2025-02-01 | [52946](https://github.com/airbytehq/airbyte/pull/52946) | Update dependencies |
| 0.2.27 | 2025-01-25 | [49292](https://github.com/airbytehq/airbyte/pull/49292) | Update dependencies |
| 0.2.26 | 2025-01-17 | [51560](https://github.com/airbytehq/airbyte/pull/51560) | Fix connection issues |
| 0.2.25 | 2024-11-25 | [48672](https://github.com/airbytehq/airbyte/pull/48672) | Update dependencies |
| 0.2.24 | 2024-10-29 | [47780](https://github.com/airbytehq/airbyte/pull/47780) | Update dependencies |
| 0.2.23 | 2024-10-28 | [47100](https://github.com/airbytehq/airbyte/pull/47100) | Update dependencies |
| 0.2.22 | 2024-10-12 | [46841](https://github.com/airbytehq/airbyte/pull/46841) | Update dependencies |
| 0.2.21 | 2024-10-05 | [46420](https://github.com/airbytehq/airbyte/pull/46420) | Update dependencies |
| 0.2.20 | 2024-09-28 | [46144](https://github.com/airbytehq/airbyte/pull/46144) | Update dependencies |
| 0.2.19 | 2024-09-21 | [45744](https://github.com/airbytehq/airbyte/pull/45744) | Update dependencies |
| 0.2.18 | 2024-09-14 | [45562](https://github.com/airbytehq/airbyte/pull/45562) | Update dependencies |
| 0.2.17 | 2024-09-07 | [45245](https://github.com/airbytehq/airbyte/pull/45245) | Update dependencies |
| 0.2.16 | 2024-08-31 | [44991](https://github.com/airbytehq/airbyte/pull/44991) | Update dependencies |
| 0.2.15 | 2024-08-24 | [44698](https://github.com/airbytehq/airbyte/pull/44698) | Update dependencies |
| 0.2.14 | 2024-08-22 | [44530](https://github.com/airbytehq/airbyte/pull/44530) | Update test dependencies |
| 0.2.13 | 2024-08-17 | [44239](https://github.com/airbytehq/airbyte/pull/44239) | Update dependencies |
| 0.2.12 | 2024-08-10 | [43682](https://github.com/airbytehq/airbyte/pull/43682) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43143](https://github.com/airbytehq/airbyte/pull/43143) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42703](https://github.com/airbytehq/airbyte/pull/42703) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42211](https://github.com/airbytehq/airbyte/pull/42211) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41789](https://github.com/airbytehq/airbyte/pull/41789) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41602](https://github.com/airbytehq/airbyte/pull/41602) | Update dependencies |
| 0.2.6 | 2024-07-09 | [41118](https://github.com/airbytehq/airbyte/pull/41118) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40854](https://github.com/airbytehq/airbyte/pull/40854) | Update dependencies |
| 0.2.4 | 2024-06-27 | [40578](https://github.com/airbytehq/airbyte/pull/40578) | Replaced deprecated AirbyteLogger with logging.Logger |
| 0.2.3 | 2024-06-25 | [40494](https://github.com/airbytehq/airbyte/pull/40494) | Update dependencies |
| 0.2.2 | 2024-06-22 | [40078](https://github.com/airbytehq/airbyte/pull/40078) | Update dependencies |
| 0.2.1 | 2024-06-06 | [39157](https://github.com/airbytehq/airbyte/pull/39157) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.0 | 2024-05-08 | [36443](https://github.com/airbytehq/airbyte/pull/36443) | Service account authentication support |
| 0.1.1 | 2024-03-05 | [35838](https://github.com/airbytehq/airbyte/pull/35838) | Un-archive connector |
| 0.1.0 | 2022-05-18 | [13118](https://github.com/airbytehq/airbyte/pull/13118) | New Destination: Firebolt |

</details>
