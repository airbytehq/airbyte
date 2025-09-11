# Discourse

This page contains the setup guide and reference information for the Discourse source connector.

## Prerequisites

- API Base URL
- API Key
- API Username

## Setup guide

### Step 1: Set up Discourse

Source Discourse is designed to interact with the data your permissions give you access to. To do so, you will need to generate a Discourse API key for an individual user.

Go to **Discourse/admin &gt; API**, and select **New API Key**.

## Step 2: Set up the Discourse connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Discourse connector and select **Discourse** from the Source type dropdown.
4. Enter your API base url, key, and the associated username that you obtained from Discourse.
5. Click **Set up source**.

## Supported sync modes

The Discourse source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Full Refresh - Overwrite + Deduped](https://docs.airbyte.com/platform/using-airbyte/core-concepts/sync-modes/full-refresh-overwrite-deduped)

## Supported Streams

This connector outputs the following streams:

- [Categories](https://docs.discourse.org/#tag/Categories/operation/listCategories)
- [Topics](https://docs.discourse.org/#tag/Topics/operation/listLatestTopics)
- [Posts](https://docs.discourse.org/#tag/Topics/operation/getTopic)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                       | Subject                                            |
| :------ | :--------- | :------------------------------------------------- | :------------------------------------------------- |
| 0.1.0   | 2025-09-09 | [TBA](https://github.com/airbytehq/airbyte/pull/#) | Initial release of Discourse connector for Airbyte |

</details>
