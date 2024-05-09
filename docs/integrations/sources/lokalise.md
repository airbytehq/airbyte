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

| Version | Date       | Pull Request                                             | Subject              |
| :------ | :--------- | :------------------------------------------------------- | :------------------- |
| 0.1.0   | 2022-10-27 | [18522](https://github.com/airbytehq/airbyte/pull/18522) | New Source: Lokalise |
