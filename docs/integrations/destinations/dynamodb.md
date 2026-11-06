# DynamoDB

This destination writes data to AWS DynamoDB.

The Airbyte DynamoDB destination allows you to sync data to AWS DynamoDB. Each stream is written to
its own table under the DynamoDB.

## Prerequisites

- For Airbyte Open Source users using the
  [Postgres](https://docs.airbyte.com/integrations/sources/postgres) source connector,
  [upgrade](https://docs.airbyte.com/operator-guides/upgrading-airbyte/) your Airbyte platform to
  version `v0.40.0-alpha` or newer and upgrade your DynamoDB connector to version `0.1.5` or newer

## Sync overview

### Output schema

Each stream will be output into its own DynamoDB table. Each table will a collections of `json`
objects containing 4 fields:

- `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
- `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
- `_airbyte_data`: a json blob representing with the extracted data.
- `sync_time`: a timestamp representing when the sync up task be triggered.

### Performance considerations

Tables created by this connector use the on-demand (`PAY_PER_REQUEST`) billing mode, so no
capacity units need to be provisioned up front. Records are written in batches of 25 items with
automatic retries for unprocessed items.

## Supported sync modes

| Sync mode | Supported? |
| :--- | :--- |
| [Full Refresh - Overwrite](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite) | Yes |
| [Full Refresh - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-append) | Yes |
| [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped) | No |
| [Incremental Sync - Append](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append) | Yes |
| [Incremental Sync - Append + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/incremental-append-deduped) | No |

## Getting started

### Requirements

1. Allow connections from Airbyte server to your AWS DynamoDB tables \(if they exist in separate
   VPCs\).
2. The credentials for AWS DynamoDB \(for the COPY strategy\).

### Setup guide

- Fill up DynamoDB info
  - **DynamoDB Endpoint**
    - Leave empty if using AWS DynamoDB, fill in endpoint URL if using customized endpoint.
  - **DynamoDB Table Name**
    - The name prefix of the DynamoDB table to store the extracted data. The table name is \\_\\_\.
  - **DynamoDB Region**
    - The region of the DynamoDB.
  - **Access Key Id**
    - See
      [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)
      on how to generate an access key.
    - We recommend creating an Airbyte-specific user. Because the connector creates one table per
      stream (and a temporary `<prefix>_airbyte_connection_test_*` table during **Test connection**),
      read/write access to existing tables is not enough: the user's
      [IAM policy](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/iam-policy-structure.html)
      must allow the following actions on `arn:aws:dynamodb:<region>:<account>:table/<prefix>_*`:
      `dynamodb:CreateTable`, `dynamodb:DescribeTable`, `dynamodb:DeleteTable`, `dynamodb:PutItem`
      and `dynamodb:BatchWriteItem`. A missing `dynamodb:CreateTable` permission results in
      `AccessDeniedException: User ... is not authorized to perform: dynamodb:CreateTable` when
      testing the connection.
  - **Secret Access Key**
    - Corresponding key to the above key id.
- Make sure your DynamoDB tables are accessible from the machine running Airbyte.
  - This depends on your networking setup.
  - You can check AWS DynamoDB documentation with a tutorial on how to properly configure your
    DynamoDB's access
    [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/access-control-overview.html).
  - The easiest way to verify if Airbyte is able to connect to your DynamoDB tables is via the check
    connection tool in the UI.

## Namespace support

This destination supports [namespaces](https://docs.airbyte.com/platform/using-airbyte/core-concepts/namespaces).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                               | Subject                                                     |
| :------ | :--------- | :--------------------------------------------------------- | :---------------------------------------------------------- |
| 0.1.8   | 2024-01-03 | [#33924](https://github.com/airbytehq/airbyte/pull/33924)  | Add new ap-southeast-3 AWS region                           |
| 0.1.7   | 2022-11-03 | [\#18672](https://github.com/airbytehq/airbyte/pull/18672) | Added strict-encrypt cloud runner                           |
| 0.1.6   | 2022-11-01 | [\#18672](https://github.com/airbytehq/airbyte/pull/18672) | Enforce to use ssl connection                               |
| 0.1.5   | 2022-08-05 | [\#15350](https://github.com/airbytehq/airbyte/pull/15350) | Added per-stream handling                                   |
| 0.1.4   | 2022-06-16 | [\#13852](https://github.com/airbytehq/airbyte/pull/13852) | Updated stacktrace format for any trace message errors      |
| 0.1.3   | 2022-05-17 | [12820](https://github.com/airbytehq/airbyte/pull/12820)   | Improved 'check' operation performance                      |
| 0.1.2   | 2022-02-14 | [10256](https://github.com/airbytehq/airbyte/pull/10256)   | Add `-XX:+ExitOnOutOfMemoryError` JVM option                |
| 0.1.1   | 2022-12-05 | [\#9314](https://github.com/airbytehq/airbyte/pull/9314)   | Rename dynamo_db_table_name to dynamo_db_table_name_prefix. |
| 0.1.0   | 2021-08-20 | [\#5561](https://github.com/airbytehq/airbyte/pull/5561)   | Initial release.                                            |

</details>