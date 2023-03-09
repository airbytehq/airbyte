# Coda

This page contains the setup guide and reference information for the Coda source connector.

## Prerequisites

You can find or create authentication tokens within [Coda](https://coda.io/account#apiSettings).

## Setup guide

## Step 1: Set up the Coda connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Coda connector and select **Coda** from the Source type dropdown.
4. Enter your `auth_token` - Coda Authentication Token with the necessary permissions \(described below\).
5. Enter your `doc_id` - Document id for a specific document created on Coda. You can check it under [Advanced Settings](https://coda.io/account)
   by exporting data and copying the id in doc_manifest.json from the downloaded zip.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `auth_token` - Coda Authentication Token with the necessary permissions \(described below\).
4. Enter your `doc_id` - Document id for a specific document created on Coda. You can check it under [Advanced Settings](https://coda.io/account)
   by exporting data and copying the id in doc_manifest.json from the downloaded zip.
5. Click **Set up source**.

## Supported sync modes

The Coda source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | No         |
| Namespaces        | No         |

## Supported Streams

- [Docs](https://coda.io/developers/apis/v1#tag/Docs/operation/listDocs)
- [Permissions](https://coda.io/developers/apis/v1#tag/Permissions/operation/getPermissions)
- [Categories](https://coda.io/developers/apis/v1#tag/Publishing/operation/listCategories)
- [Pages](https://coda.io/developers/apis/v1#tag/Pages/operation/listPages)
- [Tables](https://coda.io/developers/apis/v1#tag/Tables/operation/listTables)
- [Formulas](https://coda.io/developers/apis/v1#tag/Formulas/operation/listFormulas)
- [Controls](https://coda.io/developers/apis/v1#tag/Controls/operation/listControls)

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `integer`        | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

| Version | Date       | Pull Request                                             | Subject                          |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------- |
| 0.1.0   | 2022-11-17 | [18675](https://github.com/airbytehq/airbyte/pull/18675) | 🎉 New source: Coda [python cdk] |
