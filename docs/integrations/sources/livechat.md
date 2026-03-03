# LiveChat

This page contains the setup guide and reference information for the [LiveChat](https://www.livechat.com) source connector.

## Prerequisites

- API Username
- API Password
- Start Date

## Setup guide

### Step 1: Set up LiveChat

Source LiveChat is designed to interact with the resources your permissions give you access to. To do so, you will need to generate a LiveChat Personal Access Token (PAT) for an individual user.

- Go to **LiveChat &gt; Settings &gt; Authorization &gt; Personal Access Tokens**.
- Click the button to **create a new token**.
- Define scopes (permissions) for the token.
- Name your token (the name doesn't affect authorization).
- Click Create token.

## Step 2: Set up the LiveChat connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the LiveChat connector and select **LiveChat** from the Source type dropdown.
4. Enter your API credentials that you obtained from LiveChat, and enter the starting date you want to sync from.
5. Click **Set up source**.

## Supported sync modes

The LiveChat source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following streams:

- [Chat Engagement Report](https://platform.text.com/docs/data-reporting/reports-api#engagement)
- [Total Chats Report](https://platform.text.com/docs/data-reporting/reports-api#total-chats)
- [Queued Visitors Report](https://platform.text.com/docs/data-reporting/reports-api#queued-visitors)
- [Queued Visitors Left Report](https://platform.text.com/docs/data-reporting/reports-api#queued-visitors-left)
- [Greetings Conversion Report](https://platform.text.com/docs/data-reporting/reports-api#greetings-conversion)
- [Agent Availability Report](https://platform.text.com/docs/data-reporting/reports-api#availability)
- [Chat Response Time Report](https://platform.text.com/docs/data-reporting/reports-api#response-time)
- [Chat First Response Time Report](https://platform.text.com/docs/data-reporting/reports-api#first-response-time)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/canonical/airbyte/issues/new/choose)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                       | Subject                                            |
| :------ | :--------- | :------------------------------------------------- | :------------------------------------------------- |
| 1.0.0   | 2026-02-20 | [#50](https://github.com/canonical/airbyte/pull/#50) | Initial release of LiveChat connector for Airbyte |

</details>
