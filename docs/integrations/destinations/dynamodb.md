# DynamoDB

This destination writes data to AWS DynamoDB.

The Airbyte DynamoDB destination allows you to sync data to AWS DynamoDB. Each stream is written to its own table under the DynamoDB.

## Sync overview

### Output schema

Each stream will be output into its own DynamoDB table. Each table will a collections of `json` objects containing 4 fields:

* `_airbyte_ab_id`: a uuid assigned by Airbyte to each event that is processed.
* `_airbyte_emitted_at`: a timestamp representing when the event was pulled from the data source.
* `_airbyte_data`: a json blob representing with the extracted data.
* `sync_time`: a timestamp representing when the sync up task be triggered.

### Features

| Feature | Support | Notes |
| :--- | :---: | :--- |
| Full Refresh Sync | ✅ | Warning: this mode deletes all previously synced data in the configured DynamoDB table. |
| Incremental - Append Sync | ✅ |  |
| Incremental - Deduped History | ❌ | As this connector does not support dbt, we don't support this sync mode on this destination. |
| Namespaces | ✅ | Namespace will be used as part of the table name. |

### Performance considerations

This connector by default uses 10 capacity units for both Read and Write in DynamoDB tables. Please provision more capacity units in the DynamoDB console when there are performance constraints.

## Getting started

### Requirements

1. Allow connections from Airbyte server to your AWS DynamoDB tables \(if they exist in separate VPCs\).
2. The credentials for AWS DynamoDB \(for the COPY strategy\).

### Setup guide

* Fill up DynamoDB info
  * **DynamoDB Endpoint**
    * Leave empty if using AWS DynamoDB, fill in endpoint URL if using customized endpoint.
  * **DynamoDB Table Name**
    * The name prefix of the DynamoDB table to store the extracted data. The table name is \\_\\_\.
  * **DynamoDB Region**
    * The region of the DynamoDB.
  * **Access Key Id**
    * See [this](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys) on how to generate an access key.
    * We recommend creating an Airbyte-specific user. This user will require [read and write permissions](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_dynamodb_specific-table.html) to the DynamoDB table.
  * **Secret Access Key**
    * Corresponding key to the above key id.
* Make sure your DynamoDB tables are accessible from the machine running Airbyte.
  * This depends on your networking setup.
  * You can check AWS DynamoDB documentation with a tutorial on how to properly configure your DynamoDB's access [here](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/access-control-overview.html).
  * The easiest way to verify if Airbyte is able to connect to your DynamoDB tables is via the check connection tool in the UI.

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2021-08-20 | [\#5561](https://github.com/airbytehq/airbyte/pull/5561) | Initial release. |

