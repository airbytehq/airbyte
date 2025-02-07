# Coda

This page contains the setup guide and reference information for the Coda source connector.

## Prerequisites

You can find or create authentication tokens within [Coda](https://coda.io/account#apiSettings).

## Setup guide

## Step 1: Set up the Coda connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
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
- [Rows](https://coda.io/developers/apis/v1#tag/Rows/operation/listRows)

## Data type map

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `integer`        | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                     |
| :------ | :--------- | :------------------------------------------------------- |:------------------------------------------------------------------------------------------------------------|
| 1.3.12 | 2025-02-01 | [52841](https://github.com/airbytehq/airbyte/pull/52841) | Update dependencies |
| 1.3.11 | 2025-01-25 | [52307](https://github.com/airbytehq/airbyte/pull/52307) | Update dependencies |
| 1.3.10 | 2025-01-18 | [51692](https://github.com/airbytehq/airbyte/pull/51692) | Update dependencies |
| 1.3.9 | 2025-01-11 | [51073](https://github.com/airbytehq/airbyte/pull/51073) | Update dependencies |
| 1.3.8 | 2024-12-28 | [50550](https://github.com/airbytehq/airbyte/pull/50550) | Update dependencies |
| 1.3.7 | 2024-12-21 | [50045](https://github.com/airbytehq/airbyte/pull/50045) | Update dependencies |
| 1.3.6 | 2024-12-14 | [49485](https://github.com/airbytehq/airbyte/pull/49485) | Update dependencies |
| 1.3.5 | 2024-12-12 | [49193](https://github.com/airbytehq/airbyte/pull/49193) | Update dependencies |
| 1.3.4 | 2024-12-11 | [48304](https://github.com/airbytehq/airbyte/pull/48304) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 1.3.3 | 2024-10-29 | [47731](https://github.com/airbytehq/airbyte/pull/47731) | Update dependencies |
| 1.3.2 | 2024-10-28 | [47517](https://github.com/airbytehq/airbyte/pull/47517) | Update dependencies |
| 1.3.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.3.0 | 2024-08-15 | [44165](https://github.com/airbytehq/airbyte/pull/44165) | Refactor connector to manifest-only format |
| 1.2.13 | 2024-08-12 | [43890](https://github.com/airbytehq/airbyte/pull/43890) | Update dependencies |
| 1.2.12 | 2024-08-10 | [43516](https://github.com/airbytehq/airbyte/pull/43516) | Update dependencies |
| 1.2.11 | 2024-08-03 | [43100](https://github.com/airbytehq/airbyte/pull/43100) | Update dependencies |
| 1.2.10 | 2024-07-27 | [42741](https://github.com/airbytehq/airbyte/pull/42741) | Update dependencies |
| 1.2.9 | 2024-07-20 | [42351](https://github.com/airbytehq/airbyte/pull/42351) | Update dependencies |
| 1.2.8 | 2024-07-13 | [41892](https://github.com/airbytehq/airbyte/pull/41892) | Update dependencies |
| 1.2.7 | 2024-07-10 | [41329](https://github.com/airbytehq/airbyte/pull/41329) | Update dependencies |
| 1.2.6 | 2024-07-06 | [40810](https://github.com/airbytehq/airbyte/pull/40810) | Update dependencies |
| 1.2.5 | 2024-06-25 | [40413](https://github.com/airbytehq/airbyte/pull/40413) | Update dependencies |
| 1.2.4 | 2024-06-22 | [40091](https://github.com/airbytehq/airbyte/pull/40091) | Update dependencies |
| 1.2.3 | 2024-06-06 | [39241](https://github.com/airbytehq/airbyte/pull/39241) | [autopull] Upgrade base image to v1.2.2 |
| 1.2.2 | 2024-05-28 | [38578](https://github.com/airbytehq/airbyte/pull/38578) | Make connector Builder compatible |
| 1.2.1 | 2024-04-02 | [36775](https://github.com/airbytehq/airbyte/pull/36775) | Migrate to base image, manage dependencies with Poetry, and stop using last_records interpolation variable. |
| 1.2.0 | 2023-08-13 | [29288](https://github.com/airbytehq/airbyte/pull/29288) | Migrate python cdk to low-code |
| 1.1.0 | 2023-07-10 | [27797](https://github.com/airbytehq/airbyte/pull/27797) | Add `rows` stream |
| 1.0.0 | 2023-07-10 | [28093](https://github.com/airbytehq/airbyte/pull/28093) | Update `docs` and `pages` schemas |
| 0.1.0 | 2022-11-17 | [18675](https://github.com/airbytehq/airbyte/pull/18675) | 🎉 New source: Coda [python cdk] |

</details>
