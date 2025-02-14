# S3 Data Lake

:::caution

This connector is in early access and still evolving.
Future updates may introduce breaking changes.

We're interested in hearing about your experience! See [Github](https://github.com/airbytehq/airbyte/discussions/50404)
for more information on joining the beta.

:::

This page guides you through the process of setting up the S3 Data Lake destination connector.

This connector writes the Iceberg table format to S3, or an S3-compatible storage backend.
Currently it supports the REST, AWS Glue, and Nessie catalogs.

## Setup Guide

S3 Data Lake requires configuring two components: [S3 storage](#s3-setup), and your [Iceberg catalog](#iceberg-catalog-setup).

### S3 Setup

The connector needs certain permissions to be able to write Iceberg-format files to S3:
* `s3:ListAllMyBuckets`
* `s3:GetObject*`
* `s3:PutObject`
* `s3:PutObjectAcl`
* `s3:DeleteObject`
* `s3:ListBucket*`

### Iceberg Catalog Setup

Different catalogs have different setup requirements.

#### AWS Glue

In addition to the S3 permissions, you should also grant these Glue permissions:
* `glue:TagResource`
* `glue:UnTagResource`
* `glue:BatchCreatePartition`
* `glue:BatchDeletePartition`
* `glue:BatchDeleteTable`
* `glue:BatchGetPartition`
* `glue:CreateDatabase`
* `glue:CreateTable`
* `glue:CreatePartition`
* `glue:DeletePartition`
* `glue:DeleteTable`
* `glue:GetDatabase`
* `glue:GetDatabases`
* `glue:GetPartition`
* `glue:GetPartitions`
* `glue:GetTable`
* `glue:GetTables`
* `glue:UpdateDatabase`
* `glue:UpdatePartition`
* `glue:UpdateTable`

Set the "warehouse location" option to `s3://<bucket name>/path/within/bucket`.

The "Role ARN" option is only usable in cloud.

#### REST catalog

You will need the URI of your REST catalog.

#### Nessie

You will need the URI of your Nessie catalog, and an access token to authenticate to that catalog.

Set the "warehouse location" option to `s3://<bucket name>/path/within/bucket`.

## Iceberg schema generation

The top-level fields of the stream will be mapped to Iceberg fields. Nested fields (objects, arrays, and unions) will be
mapped to `STRING` columns, and written as serialized JSON. This is the full mapping between Airbyte types and Iceberg types:

| Airbyte type               | Iceberg type                   |
|----------------------------|--------------------------------|
| Boolean                    | Boolean                        |
| Date                       | Date                           |
| Integer                    | Long                           |
| Number                     | Double                         |
| String                     | String                         |
| Time with timezone         | Time                           |
| Time without timezone      | Time                           |
| Timestamp with timezone    | Timestamp with timezone        |
| Timestamp without timezone | Timestamp without timezone     |
| Object                     | String (JSON-serialized value) |
| Array                      | String (JSON-serialized value) |
| Union                      | String (JSON-serialized value) |

Note that for the time/timestamp with timezone types, the value is first adjusted to UTC, and then
written into the Iceberg file.

### Schema evolution

This connector supports limited schema evolution. Outside of refreshes/clears, the connector will never
rewrite existing data files. This means that we can only handle specific schema changes:
* Adding/removing a column
* Widening columns
* Changing the primary key

If your source goes through an unsupported schema change, the connector will fail at sync time.
To resolve this, you can either:
* Manually edit your table schema via Iceberg directly
* Refresh your connection (removing existing records) / clear your connection

Full refresh overwrite syncs can also handle these schema changes transparently.

## Deduplication

This connector uses a merge-on-read strategy to support deduplication:
* The stream's primary keys are translated to Iceberg's [identifier columns](https://iceberg.apache.org/spec/#identifier-field-ids).
* An "upsert" is an [equality-based delete](https://iceberg.apache.org/spec/#equality-delete-files)
  on that row's primary key, followed by an insertion of the new data.

### Assumptions

The S3 Data Lake connector assumes that one of two things is true:
* The source will never emit the same primary key twice in a single sync attempt
* If the source emits the same PK multiple times in a single attempt, it will always emit those records
  in cursor order (oldest to newest)

If these conditions are not met, you may see inaccurate data in the destination (i.e. older records
taking precendence over newer records). If this happens, you should use the `append` or `overwrite`
sync mode.

## Branching

Iceberg supports [Git-like semantics](https://iceberg.apache.org/docs/latest/branching/) over your data.
Most query engines target the `main` branch.

This connector leverages those semantics to provide resilient syncs:
* Within each sync, each microbatch creates a new snapshot
* During truncate syncs, the connector writes the refreshed data to the `airbyte_staging` branch,
  and fast-forwards the `main` branch at the end of the sync.
  * This means that your data remains queryable right up to the end of a truncate sync, at which point
    it is atomically swapped to the updated version.

## Catalog-specific information

### AWS Glue

If you have an existing Glue table, and you want to replace that table with an Airbyte-managed Iceberg table,
you must first drop the Glue table. Otherwise you will encounter an error `Input Glue table is not an iceberg table: <your table name>`.

Note that dropping Glue tables from the console [may not immediately delete them](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/batch_delete_table.html).
You must either wait for AWS to finish their background processing, or manually call the AWS API to
drop all table versions.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                      |
|:--------|:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------------|
| 0.3.13  | 2025-02-14 | [\#53697](https://github.com/airbytehq/airbyte/pull/53697) | Internal refactor                                                            |
| 0.3.12  | 2025-02-12 | [\#53170](https://github.com/airbytehq/airbyte/pull/53170) | Improve documentation, tweak error handling of invalid schema evolution      |
| 0.3.11  | 2025-02-12 | [\#53216](https://github.com/airbytehq/airbyte/pull/53216) | Support arbitrary schema change in overwrite / truncate refresh / clear sync |
| 0.3.10  | 2025-02-11 | [\#53622](https://github.com/airbytehq/airbyte/pull/53622) | Enable the Nessie integration tests                                          |
| 0.3.9   | 2025-02-10 | [\#53165](https://github.com/airbytehq/airbyte/pull/53165) | Very basic usability improvements and documentation                          |
| 0.3.8   | 2025-02-10 | [\#52666](https://github.com/airbytehq/airbyte/pull/52666) | Change the chunk size to 1.5Gb                                               |
| 0.3.7   | 2025-02-07 | [\#53141](https://github.com/airbytehq/airbyte/pull/53141) | Adding integration tests around the Rest catalog                             |
| 0.3.6   | 2025-02-06 | [\#53172](https://github.com/airbytehq/airbyte/pull/53172) | Internal refactor                                                            |
| 0.3.5   | 2025-02-06 | [\#53164](https://github.com/airbytehq/airbyte/pull/53164) | Improve error message on null primary key in dedup mode                      |
| 0.3.4   | 2025-02-05 | [\#53173](https://github.com/airbytehq/airbyte/pull/53173) | Tweak spec wording                                                           |
| 0.3.3   | 2025-02-05 | [\#53176](https://github.com/airbytehq/airbyte/pull/53176) | Fix time_with_timezone handling (values are now adjusted to UTC)             |
| 0.3.2   | 2025-02-04 | [\#52690](https://github.com/airbytehq/airbyte/pull/52690) | Handle special characters in stream name/namespace when using AWS Glue       |
| 0.3.1   | 2025-02-03 | [\#52633](https://github.com/airbytehq/airbyte/pull/52633) | Fix dedup                                                                    |
| 0.3.0   | 2025-01-31 | [\#52639](https://github.com/airbytehq/airbyte/pull/52639) | Make the database/namespace a required field                                 |
| 0.2.23  | 2025-01-27 | [\#51600](https://github.com/airbytehq/airbyte/pull/51600) | Internal refactor                                                            |
| 0.2.22  | 2025-01-22 | [\#52081](https://github.com/airbytehq/airbyte/pull/52081) | Implement support for REST catalog                                           |
| 0.2.21  | 2025-01-27 | [\#52564](https://github.com/airbytehq/airbyte/pull/52564) | Fix crash on stream with 0 records                                           |
| 0.2.20  | 2025-01-23 | [\#52068](https://github.com/airbytehq/airbyte/pull/52068) | Add support for default namespace (/database name)                           |
| 0.2.19  | 2025-01-16 | [\#51595](https://github.com/airbytehq/airbyte/pull/51595) | Clarifications in connector config options                                   |
| 0.2.18  | 2025-01-15 | [\#51042](https://github.com/airbytehq/airbyte/pull/51042) | Write structs as JSON strings instead of Iceberg structs.                    |
| 0.2.17  | 2025-01-14 | [\#51542](https://github.com/airbytehq/airbyte/pull/51542) | New identifier fields should be marked as required.                          |
| 0.2.16  | 2025-01-14 | [\#51538](https://github.com/airbytehq/airbyte/pull/51538) | Update identifier fields if incoming fields are different than existing ones |
| 0.2.15  | 2025-01-14 | [\#51530](https://github.com/airbytehq/airbyte/pull/51530) | Set AWS region for S3 bucket for nessie catalog                              |
| 0.2.14  | 2025-01-14 | [\#50413](https://github.com/airbytehq/airbyte/pull/50413) | Update existing table schema based on the incoming schema                    |
| 0.2.13  | 2025-01-14 | [\#50412](https://github.com/airbytehq/airbyte/pull/50412) | Implement logic to determine super types between iceberg types               |
| 0.2.12  | 2025-01-10 | [\#50876](https://github.com/airbytehq/airbyte/pull/50876) | Add support for AWS instance profile auth                                    |
| 0.2.11  | 2025-01-10 | [\#50971](https://github.com/airbytehq/airbyte/pull/50971) | Internal refactor in AWS auth flow                                           |
| 0.2.10  | 2025-01-09 | [\#50400](https://github.com/airbytehq/airbyte/pull/50400) | Add S3DataLakeTypesComparator                                                |
| 0.2.9   | 2025-01-09 | [\#51022](https://github.com/airbytehq/airbyte/pull/51022) | Rename all classes and files from Iceberg V2                                 |
| 0.2.8   | 2025-01-09 | [\#51012](https://github.com/airbytehq/airbyte/pull/51012) | Rename/Cleanup package from Iceberg V2                                       |
| 0.2.7   | 2025-01-09 | [\#50957](https://github.com/airbytehq/airbyte/pull/50957) | Add support for GLUE RBAC (Assume role)                                      |
| 0.2.6   | 2025-01-08 | [\#50991](https://github.com/airbytehq/airbyte/pull/50991) | Initial public release.                                                      |

</details>
