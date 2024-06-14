# SurveyCTO

This page guides you through the process of setting up the SurveyCTO source connector.

## Prerequisites

- Server Name `The name of the ServerCTO server`
- Your SurveyCTO `Username`
- Your SurveyCTO `Password`
- Form ID `Unique Identifier for one of your forms`
- Start Date `Start Date default`

## How to setup a SurveyCTO Account

- create the account
- create your form
- publish your form
- give your user an API consumer permission to the existing role or create a user with that role and permission.

## Set up the SurveyCTO source connection

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Survey CTO** from the Source type dropdown.
4. Enter a name for your source.
5. Enter a Server name for your SurveyCTO account.
6. Enter a Username for SurveyCTO account.
7. Enter a Password for SurveyCTO account.
8. Form ID's (We can multiple forms id here to pull from)
9. Start Date (This can be pass to pull the data from particular date)
10. Click **Set up source**.

## Supported sync modes

The SurveyCTO source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- (Recommended)[ Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

The SurveyCTO source connector supports the following streams:

- Surveycto

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                    |
| ------- | ---------- | -------------------------------------------------------- | -------------------------- |
| 0.1.4 | 2024-06-04 | [38993](https://github.com/airbytehq/airbyte/pull/38993) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.3 | 2024-05-20 | [38439](https://github.com/airbytehq/airbyte/pull/38439) | [autopull] base image + poetry + up_to_date |
| 0.1.2 | 2023-07-27 | [28512](https://github.com/airbytehq/airbyte/pull/28512) | Added Check Connection |
| 0.1.1 | 2023-04-25 | [24784](https://github.com/airbytehq/airbyte/pull/24784) | Fix incremental sync |
| 0.1.0 | 2022-11-16 | [19371](https://github.com/airbytehq/airbyte/pull/19371) | SurveyCTO Source Connector |

</details>