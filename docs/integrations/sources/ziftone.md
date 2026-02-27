# ZiftONE

This page contains the setup guide and reference information for the [ZiftONE](https://supplier.ziftone.com/) source connector.

## Prerequisites

- API Base URL (`https://supplier.ziftone.com/api/`)
- Username and password, provided by an administrator to your ZiftONE organization.

## Setup guide

### Step 1: Set up ZiftONE

A user with the appropriate permissions needs to be created in your ZiftONE organization.

### Step 2: Set up the ZiftONE connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Github connector and select **ZiftONE** from the Source type dropdown.
4. To authenticate, populate the **ZiftONE Username** and **ZiftONE Password** fields with the account credentials provided by your ZiftONE administrator.

## Supported sync modes

The ZiftONE source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported Streams

This connector outputs the following incremental streams:

- [Deals](https://developers.ziftone.com/reference/getdeals)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                         | Subject                                            |
| :------ | :--------- | :--------------------------------------------------- | :------------------------------------------------- |
| 0.1.0   | 2026-02-23 | [#51](https://github.com/canonical/airbyte/pull/#51) | Initial release of ZiftONE connector for Airbyte   |

</details>
