# LexOffice

This page guides you through the process of setting up the LexOffice source connector.

## Prerequisites

- API Key `The API key obtained from LexOffice`
- Start Date `The date to start synchronization at`
- Voucher Type `To filter vouchers by type`
- Voucher Status `To filter vouchers by status`

## How to setup a LexOffice Account
- create the account at [LexOffice](https://www.lexoffice.de)
- create your API key [here](https://api.lexoffice.io)

## Set up the LexOffice source connection
1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **LexOffice** from the Source type dropdown.
4. Enter a name for your source.
5. Enter the API key for your LexOffice account.
6. Enter Start Date (This can be pass to pull the data from particular date)
7. Enter Voucher Type (This can be passed to pull the data of particular type)
8. Enter Voucher Status (This can be passed to pull the data of particular status)
9. Click **Set up source**.

## Supported sync modes

The LexOffice source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* (Recommended)[ Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams

The LexOffice source connector supports the following streams:

- Vouchers

## Changelog

| Version | Date | Pull Request | Subject |
| 0.1.0   | 2022-11-27 | [19817](https://github.com/airbytehq/airbyte/pull/19817)   | LexOffice Source Connector |