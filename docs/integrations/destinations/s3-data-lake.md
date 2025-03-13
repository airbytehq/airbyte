# S3 Data Lake

This page guides you through setting up the S3 Data Lake destination connector. 

This connector writes the Iceberg table format to S3 or an S3-compatible storage backend using a supported Iceberg catalog. This is Airbyte's preferred Iceberg integration. It replaces the older [Iceberg](iceberg) and [S3-Glue](s3-glue) destinations, performs better, and implements Airbyte's newer core features. You should switch to this destination when you can.

## Prerequisites

The S3 Data Lake connector requires two things.

1. An S3 storage bucket or S3-compatible storage backend.
2. A supported Iceberg catalog. Currently, the connector supports these catalogs:

    - REST
    - AWS Glue
    - Nessie

## Setup guide

Follow these steps to set up your S3 storage and Iceberg catalog permissions.

### S3 setup and permissions

S3 setup consists of creating a bucket policy and authenticating.

#### Create a bucket policy

Create a bucket policy.

1. Open the [IAM console](https://console.aws.amazon.com/iam/home#home).
2. In the IAM dashboard, select **Policies** > **Create Policy**.
3. Select the **JSON** tab and paste the following JSON into the Policy editor. Substitute your own bucket name on the highlighted lines.

    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "s3:ListAllMyBuckets",
            "s3:GetObject*",
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:DeleteObject",
            "s3:ListBucket*"
          ],
          "Resource": [
            // highlight-next-line
            "arn:aws:s3:::YOUR_BUCKET_NAME/*",
            // highlight-next-line
            "arn:aws:s3:::YOUR_BUCKET_NAME"
          ]
        }
      ]
    }
    ```

    :::note
    Object-level permissions alone aren't sufficient to authenticate. Include **bucket-level** permissions as provided in the preceding example.
    :::

4. Click **Next**, give your policy a descriptive name, then click **Create policy**.

#### Authenticate {#authentication-s3}

In most cases, you authenticate with an IAM user. If you're using Airbyte Cloud with the Glue catalog, you can authenticate with an IAM role.

<details>
  <summary>Authenticate with an IAM user (Self-Managed or Cloud, with any catalog)</summary>

Use an existing or new [Access Key ID and Secret Access Key](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html).

1. In the IAM dashboard, click **Users**.

2. If you're using an existing IAM user, select that user, then click **Add permissions** > **Add permission**. If you're creating a new user, click **Add users**.

3. Click **Attach policies directly**, then check the box for your policy. Click **Next** > **Add permissions**.

4. Click the **Security credentials** tab > **Create access key**. The AWS console prompts you to select a use case and add optional tags to your access key.

5. Click **Create access key**. Take note of your keys.

6. In Airbyte, enter those keys into the Airbyte connector's **AWS Access Key ID** and **AWS Secret Access Key** fields.

</details>

<!-- env:cloud -->
<details>
<summary>Authenticate with an IAM role (Cloud with Glue catalog only)</summary>

:::note
To use S3 authentication with an IAM role, an Airbyte team member must enable it. If you'd like to use this feature, [contact the Sales team](https://airbyte.com/company/talk-to-sales).
:::

1. In the IAM dashboard, click **Roles**, then **Create role**.

2. Choose the **AWS account** trusted entity type.

3. Set up a trust relationship for the role. This allows the Airbyte instance's AWS account to assume this role. You also need to specify an external ID, which is a secret key that the trusting service (Airbyte) and the trusted role (the role you're creating) both know. This ID prevents the "confused deputy" problem. The External ID should be your Airbyte workspace ID, which you can find in the URL of your workspace page. Edit the trust relationship policy to include the external ID:

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::094410056844:user/delegated_access_user"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "sts:ExternalId": "{your-airbyte-workspace-id}"
                    }
                }
            }
        ]
    }
    ```

4. Complete the role creation and save the Role ARN for later.

5. Select **Attach policies directly**, then find and check the box for your new policy. Click **Next**, then **Add permissions**.

6. In Airbyte, select **Glue** as the catalog and enter the Role ARN into the **Role ARN** field.

</details>

<!-- /env:cloud -->

### Iceberg catalog setup and permissions

The rest of the setup process differs depending on the catalog you're using.

#### REST

Enter the URI of your REST catalog. You may also need to enter the default namespace.

#### AWS Glue

1. Update your S3 policy, created previously, to grant these Glue permissions.

    ```json
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "s3:ListAllMyBuckets",
            "s3:GetObject*",
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:DeleteObject",
            "s3:ListBucket*",
            // highlight-start
            "glue:TagResource",
            "glue:UnTagResource",
            "glue:BatchCreatePartition",
            "glue:BatchDeletePartition",
            "glue:BatchDeleteTable",
            "glue:BatchGetPartition",
            "glue:CreateDatabase",
            "glue:CreateTable",
            "glue:CreatePartition",
            "glue:DeletePartition",
            "glue:DeleteTable",
            "glue:GetDatabase",
            "glue:GetPartition",
            "glue:GetPartitions",
            "glue:GetTable",
            "glue:GetTables",
            "glue:UpdateDatabase",
            "glue:UpdatePartition",
            "glue:UpdateTable"
            // highlight-end
          ],
          "Resource": [
            "arn:aws:s3:::YOUR_BUCKET_NAME/*",
            "arn:aws:s3:::YOUR_BUCKET_NAME"
          ]
        }
      ]
    }
    ```

2. Set the **warehouse location** option to `s3://<bucket name>/path/within/bucket`.

3. If you're using Airbyte Cloud and authenticating with an IAM role, set the **Role ARN** option to the value you noted earlier while [setting up authentication](#authentication-s3) on S3.

4. If you have an existing Glue table and you want to replace that table with an Airbyte-managed Iceberg table, drop the Glue table. If you don't, you'll encounter the error `Input Glue table is not an iceberg table: <your table name>`.

    Dropping Glue tables from the console [may not immediately delete them](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue/client/batch_delete_table.html). Either wait for AWS to finish their background processing, or use the AWS API to drop all table versions.

#### Nessie

To authenticate with Nessie, do two things.

1. Set the URI of your Nessie catalog and an access token to authenticate to that catalog.

2. Set the **Warehouse location** option to `s3://<bucket name>/path/within/bucket`.

## Output schema

### How Airbyte generates the Iceberg schema

In each stream, Airbyte maps top-level fields to Iceberg fields. Airbyte maps nested fields (objects, arrays, and unions) to string columns and writes them as serialized JSON. 

This is the full mapping between Airbyte types and Iceberg types.

| Airbyte type               | Iceberg type                   |
| -------------------------- | ------------------------------ |
| Boolean                    | Boolean                        |
| Date                       | Date                           |
| Integer                    | Long                           |
| Number                     | Double                         |
| String                     | String                         |
| Time with timezone*         | Time                           |
| Time without timezone      | Time                           |
| Timestamp with timezone*    | Timestamp with timezone        |
| Timestamp without timezone | Timestamp without timezone     |
| Object                     | String (JSON-serialized value) |
| Array                      | String (JSON-serialized value) |
| Union                      | String (JSON-serialized value) |

*Airbyte converts the `time with timezone` and `timestamp with timezone` types to Coordinated Universal Time (UTC) before writing to the Iceberg file.

### Managing schema evolution

This connector never rewrites existing Iceberg data files. This means Airbyte can only handle specific source schema changes.

- Adding or removing a column
- Widening a column
- Changing the primary key

You have the following options to manage schema evolution.

- To handle unsupported schema changes automatically, use [Full Refresh - Overwrite](../../using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) as your [sync mode](../../using-airbyte/core-concepts/sync-modes).
- To handle unsupported schema changes as they occur, wait for a sync to fail, then take action to restore it. Either:

    - Manually edit your table schema in Iceberg directly.
    - [Refresh](../../operator-guides/refreshes) your connection in Airbyte.
    - [Clear](../../operator-guides/clear) your connection in Airbyte.

## Deduplication

This connector uses a merge-on-read strategy to support deduplication.

- Airbyte translates the stream's primary keys to Iceberg's [identifier columns](https://iceberg.apache.org/spec/#identifier-field-ids).
- An "upsert" is an [equality-based delete](https://iceberg.apache.org/spec/#equality-delete-files) on that row's primary key, followed by an insertion of the new data.

### Assumptions about primary keys

The S3 Data Lake connector assumes that one of two things is true:

- The source never emits the same primary key twice in a single sync attempt.
- If the source emits the same primary key multiple times in a single attempt, it always emits those records in cursor order from oldest to newest.

If these conditions aren't met, you may see inaccurate data in Iceberg in the form of older records taking precedence over newer records. If this happens, use append or overwrite as your [sync modes](../../using-airbyte/core-concepts/sync-modes/).

An unknown number of API sources have streams that don't meet these conditions. Airbyte knows [Stripe](../sources/stripe) and [Monday](../sources/monday) don't, but there are probably others.

## Branching and data availability

Iceberg supports [Git-like semantics](https://iceberg.apache.org/docs/latest/branching/) over your data. This connector leverages those semantics to provide resilient syncs.

- In each sync, each microbatch creates a new snapshot.

- During truncate syncs, the connector writes the refreshed data to the `airbyte_staging` branch and fast-forwards the `main` branch at the end of the sync. Since most query engines target the `main` branch,  people can query your data until the end of a truncate sync, at which point it's atomically swapped to the new version.

## Considerations and limitations

This section documents known considerations and limitations about how this Iceberg destination interacts with other products.

### Snowflake

Airbyte uses Iceberg row-level deletes to mark older versions of records as outdated. If you're using Iceberg tables for Snowflake, Snowflake doesn't recognize native Iceberg row-level deletes for Iceberg tables with external catalogs like Glue ([see Snowflake's docs](https://docs.snowflake.com/en/user-guide/tables-iceberg#considerations-and-limitations)). As a result, your query results return all versions of a record.

For example, the following table contains three versions of the 'Alice' record.

| `id` | `name` | `updated_at`     | `_airbyte_extracted_at` |
| :--- | :----- | :--------------- | :---------------------- |
| 1    | Alice  | 2024-03-01 10:00 | 2024-03-01 10:10        |
| 1    | Alice  | 2024-03-02 12:00 | 2024-03-02 12:10        |
| 1    | Alice  | 2024-03-03 14:00 | 2024-03-03 14:10        |

To mitigate this, generate a flag to detect outdated records. Airbyte generates an `airbyte_extracted_at` [metadata field](../../understanding-airbyte/airbyte-metadata-fields.md) that assists with this.

```sql
row_number() over (partition by {primary_key} order by {cursor}, _airbyte_extracted_at)) != 1 OR _ab_cdc_deleted_at IS NOT NULL as is_outdated;
```

Now, you can identify the latest version of the 'Alice' record by querying whether `is_outdated` is false.

| `id` | `name` | `updated_at`     | `_airbyte_extracted_at` | `row_number` | `is_outdated` |
| :--- | :----- | :--------------- | :---------------------- | ------------ | ------------- |
| 1    | Alice  | 2024-03-01 10:00 | 2024-03-01 10:10        | 3            | True          |
| 1    | Alice  | 2024-03-02 12:00 | 2024-03-02 12:10        | 2            | True          |
| 1    | Alice  | 2024-03-03 14:00 | 2024-03-03 14:10        | 1            | False         |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                                      |
| :------ | :--------- | :--------------------------------------------------------- | :--------------------------------------------------------------------------- |
| 0.3.15  | 2025-02-28 | [\#54724](https://github.com/airbytehq/airbyte/pull/54724) | Certify connector                                                            |
| 0.3.14  | 2025-02-14 | [\#53241](https://github.com/airbytehq/airbyte/pull/53241) | New CDK interface; perf improvements, skip initial record staging            |
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
