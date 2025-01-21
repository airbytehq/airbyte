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
| 0.4.8 | 2025-01-18 | [51973](https://github.com/airbytehq/airbyte/pull/51973) | Update dependencies |
| 0.4.7 | 2025-01-11 | [51459](https://github.com/airbytehq/airbyte/pull/51459) | Update dependencies |
| 0.4.6 | 2024-12-28 | [50812](https://github.com/airbytehq/airbyte/pull/50812) | Update dependencies |
| 0.4.5 | 2024-12-21 | [50359](https://github.com/airbytehq/airbyte/pull/50359) | Update dependencies |
| 0.4.4 | 2024-12-14 | [49755](https://github.com/airbytehq/airbyte/pull/49755) | Update dependencies |
| 0.4.3 | 2024-12-12 | [49417](https://github.com/airbytehq/airbyte/pull/49417) | Update dependencies |
| 0.4.2 | 2024-12-11 | [47545](https://github.com/airbytehq/airbyte/pull/47545) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.4.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.4.0 | 2024-08-14 | [44058](https://github.com/airbytehq/airbyte/pull/44058) | Refactor connector to manifest-only format |
| 0.3.14 | 2024-08-12 | [43843](https://github.com/airbytehq/airbyte/pull/43843) | Update dependencies |
| 0.3.13 | 2024-08-10 | [43466](https://github.com/airbytehq/airbyte/pull/43466) | Update dependencies |
| 0.3.12 | 2024-08-03 | [43152](https://github.com/airbytehq/airbyte/pull/43152) | Update dependencies |
| 0.3.11 | 2024-07-27 | [42778](https://github.com/airbytehq/airbyte/pull/42778) | Update dependencies |
| 0.3.10 | 2024-07-20 | [42178](https://github.com/airbytehq/airbyte/pull/42178) | Update dependencies |
| 0.3.9 | 2024-07-15 | [38790](https://github.com/airbytehq/airbyte/pull/38790) | Make compatible with the builder |
| 0.3.8 | 2024-07-13 | [41687](https://github.com/airbytehq/airbyte/pull/41687) | Update dependencies |
| 0.3.7 | 2024-07-10 | [41357](https://github.com/airbytehq/airbyte/pull/41357) | Update dependencies |
| 0.3.6 | 2024-07-09 | [41307](https://github.com/airbytehq/airbyte/pull/41307) | Update dependencies |
| 0.3.5 | 2024-07-06 | [40862](https://github.com/airbytehq/airbyte/pull/40862) | Update dependencies |
| 0.3.4 | 2024-06-25 | [40336](https://github.com/airbytehq/airbyte/pull/40336) | Update dependencies |
| 0.3.3 | 2024-06-22 | [40022](https://github.com/airbytehq/airbyte/pull/40022) | Update dependencies |
| 0.3.2 | 2024-05-21 | [38488](https://github.com/airbytehq/airbyte/pull/38488) | [autopull] base image + poetry + up_to_date |
| 0.3.1 | 2023-03-06 | [23231](https://github.com/airbytehq/airbyte/pull/23231) | Publish using low-code CDK Beta version |
| 0.3.0 | 2022-11-02 | [18936](https://github.com/airbytehq/airbyte/pull/18936) | Migrate to low code + certify to Beta + migrate to API v4 |
| 0.2.6 | 2022-09-08 | [16361](https://github.com/airbytehq/airbyte/pull/16361) | Avoid infinite loop for non-paginated APIs |
| 0.2.4 | 2021-11-08 | [7649](https://github.com/airbytehq/airbyte/pull/7649) | Migrate to the CDK |

</details>
