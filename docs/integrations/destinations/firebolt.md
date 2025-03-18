# Firebolt

This page guides you through the process of setting up the Firebolt destination connector.

## Prerequisites

This Firebolt destination connector has two replication strategies:

1. SQL: Replicates data via SQL INSERT queries. This leverages
   [Firebolt SDK](https://pypi.org/project/firebolt-sdk/) to execute queries directly on Firebolt
   [Engines](https://docs.firebolt.io/godocs/Overview/understanding-engine-fundamentals.html).
   **Not recommended for production workloads as this does not scale well**.

2. S3: Replicates data by first uploading data to an S3 bucket, creating an External Table and
   writing into a final Fact Table. This is the recommended loading
   [approach](https://docs.firebolt.io/godocs/Guides/loading-data/loading-data.html). Requires an S3 bucket and
   credentials in addition to Firebolt credentials.

For SQL strategy:

- **Host**
- **Username**
- **Password**
- **Database**
- **Account**
- **Engine**

Airbyte automatically picks an approach depending on the given configuration - if S3 configuration
is present, Airbyte will use the S3 strategy.

For S3 strategy:

- **Username**
- **Password**
- **Database**
- **Account**
- **S3 Bucket Name**
  - See [this](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) to
    create an S3 bucket.
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
- **Host (optional)**
  - Firebolt backend URL. Can be left blank for most usecases.
- **Engine (optional)**
  - If connecting to a non-default engine you should specify its name or url here.

## Setup guide

1. Sign up to Firebolt following the
   [guide](https://docs.firebolt.io/godocs/Guides/managing-your-organization/creating-an-organization.html)
1. Follow the getting started [tutorial](https://docs.firebolt.io/godocs/Guides/getting-started.html) to setup a database.
1. Create a [service account](https://docs.firebolt.io/godocs/Guides/managing-your-organization/service-accounts.html).
1. Create an engine as described in
   [here](https://docs.firebolt.io/godocs/Guides/working-with-engines/working-with-engines-using-the-firebolt-manager.html)
1. (Optional)
   [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) a
   staging S3 bucket \(for the S3 strategy\).
1. (Optional)
   [Create](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-iam-policies.html) an IAM
   with programmatic access to read, write and delete objects from an S3 bucket.

## Supported sync modes

The Firebolt destination connector supports the following
[sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):

- Full Refresh
- Incremental - Append Sync

## Connector-specific features & highlights

### Output schema

Each stream will be output into its own raw
[Fact table](https://docs.firebolt.io/working-with-tables.html#fact-and-dimension-tables) in
Firebolt. Each table will contain 3 columns:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed. The column type in
  Firebolt is `VARCHAR`.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
  The column type in Firebolt is `TIMESTAMP`.
- `_airbyte_data`: a json blob representing the event data. The column type in Firebolt is `VARCHAR`
  but can be parsed with JSON functions.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                |
|:--------| :--------- | :------------------------------------------------------- | :------------------------------------- |
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
