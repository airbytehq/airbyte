# Lokalise

This page contains the setup guide and reference information for the [Lokalise](https://lokalise.com/) source connector.

You can find more information about the Lokalise REST API [here](https://developers.lokalise.com/reference/lokalise-rest-api).

## Prerequisites

You can find your Project ID and find or create an API key within [Lokalise](https://docs.lokalise.com/en/articles/1929556-api-tokens).

## Setup guide

## Step 1: Set up the Lokalise connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Lokalise connector and select **Lokalise** from the Source type dropdown.
4. Enter your `project_id` - Lokalise Project ID.
5. Enter your `api_key` - Lokalise API key with read permissions.
6. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
3. Enter your `project_id` - Lokalise Project ID.
4. Enter your `api_key` - Lokalise API key with read permissions.
5. Click **Set up source**.

## Supported sync modes

The Lokalise source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |
| SSL connection    | Yes        |
| Namespaces        | No         |

## Supported Streams

- [Keys](https://developers.lokalise.com/reference/list-all-keys)
- [Languages](https://developers.lokalise.com/reference/list-project-languages)
- [Comments](https://developers.lokalise.com/reference/list-project-comments)
- [Contributors](https://developers.lokalise.com/reference/list-all-contributors)
- [Translations](https://developers.lokalise.com/reference/list-all-translations)

## Data type map

| Integration Type    | Airbyte Type |
| :------------------ | :----------- |
| `string`            | `string`     |
| `integer`, `number` | `number`     |
| `array`             | `array`      |
| `object`            | `object`     |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject              |
| :------ | :--------- | :------------------------------------------------------- | :------------------- |
| 0.2.7 | 2025-01-11 | [51204](https://github.com/airbytehq/airbyte/pull/51204) | Update dependencies |
| 0.2.6 | 2024-12-28 | [50635](https://github.com/airbytehq/airbyte/pull/50635) | Update dependencies |
| 0.2.5 | 2024-12-21 | [50121](https://github.com/airbytehq/airbyte/pull/50121) | Update dependencies |
| 0.2.4 | 2024-12-14 | [49216](https://github.com/airbytehq/airbyte/pull/49216) | Update dependencies |
| 0.2.3 | 2024-12-11 | [48995](https://github.com/airbytehq/airbyte/pull/48995) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.2.2 | 2024-11-04 | [47935](https://github.com/airbytehq/airbyte/pull/47935) | Update dependencies |
| 0.2.1 | 2024-10-28 | [47629](https://github.com/airbytehq/airbyte/pull/47629) | Update dependencies |
| 0.2.0 | 2024-08-26 | [44765](https://github.com/airbytehq/airbyte/pull/44765) | Refactor connector to manifest-only format |
| 0.1.15 | 2024-08-24 | [44696](https://github.com/airbytehq/airbyte/pull/44696) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44203](https://github.com/airbytehq/airbyte/pull/44203) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43917](https://github.com/airbytehq/airbyte/pull/43917) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43699](https://github.com/airbytehq/airbyte/pull/43699) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43121](https://github.com/airbytehq/airbyte/pull/43121) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42644](https://github.com/airbytehq/airbyte/pull/42644) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42307](https://github.com/airbytehq/airbyte/pull/42307) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41803](https://github.com/airbytehq/airbyte/pull/41803) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41395](https://github.com/airbytehq/airbyte/pull/41395) | Update dependencies |
| 0.1.6 | 2024-07-09 | [41188](https://github.com/airbytehq/airbyte/pull/41188) | Update dependencies |
| 0.1.5 | 2024-07-06 | [40809](https://github.com/airbytehq/airbyte/pull/40809) | Update dependencies |
| 0.1.4 | 2024-06-25 | [40337](https://github.com/airbytehq/airbyte/pull/40337) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40178](https://github.com/airbytehq/airbyte/pull/40178) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39168](https://github.com/airbytehq/airbyte/pull/39168) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38435](https://github.com/airbytehq/airbyte/pull/38435) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-10-27 | [18522](https://github.com/airbytehq/airbyte/pull/18522) | New Source: Lokalise |

</details>
