# Tempo

This page contains the setup guide and reference information for the Tempo source connector.

## Prerequisites

- API Token

## Setup guide

### Step 1: Set up Tempo

Source Tempo is designed to interact with the data your permissions give you access to. To do so, you will need to generate a Tempo OAuth 2.0 token for an individual user.

Go to **Tempo &gt; Settings**, scroll down to **Data Access** and select **API integration**.

## Step 2: Set up the Tempo connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Tempo connector and select **Tempo** from the Source type dropdown.
4. Enter your API token that you obtained from Tempo.
5. Click **Set up source**.

## Supported sync modes

The Tempo source connector supports the following [ sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following streams:

- [Accounts](https://apidocs.tempo.io/#tag/Accounts)
- [Customers](https://apidocs.tempo.io/#tag/Customers)
- [Worklogs](https://apidocs.tempo.io/#tag/Worklogs)
- [Workload Schemes](https://apidocs.tempo.io/#tag/Workload-Schemes)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                   |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------- |
| 0.3.2 | 2024-05-21 | [38488](https://github.com/airbytehq/airbyte/pull/38488) | [autopull] base image + poetry + up_to_date |
| 0.3.1   | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version                   |
| 0.3.0   | 2022-11-02 | [18936](https://github.com/airbytehq/airbyte/pull/18936) | Migrate to low code + certify to Beta + migrate to API v4 |
| 0.2.6   | 2022-09-08 | [16361](https://github.com/airbytehq/airbyte/pull/16361) | Avoid infinite loop for non-paginated APIs                |
| 0.2.4   | 2021-11-08 | [7649](https://github.com/airbytehq/airbyte/pull/7649)   | Migrate to the CDK                                        |

</details>
