# Tenkft

This is a setup guide for the Tenkft source connector which collects data from [its API](https://10kft.github.io/10kft-api/).

## Prerequisites

An API key is required. See the [Tenkft Authentication API section](https://10kft.github.io/10kft-api/#authentication) for more information.

## Setup guide

## Step 1: Set up the Tenkft connector in Airbyte

### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Tenkft connector and select **Tenkft** from the Source type dropdown.
4. Enter your `api_key` - Tenkft API key.
5. Enter your `per_page` - Optional. It should not exceed 1000 rows.
6. Enter your `page` - Optional. Number of Pages.
7. Enter your `start_date` - Optional. Start date to filter records when collecting data.
8. Enter your `end_date` - Optional. End date to filter records when collecting data.
9. Enter your `query` - Optional. Type your query to filter records when collecting data.
10. Click **Set up source**.

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source. 
3. Enter your `api_key` - Tenkft API key. 
4. Enter your `per_page` - Optional. It should not exceed 1000 rows.
5. Enter your `page` - Optional. Number of Pages.
6. Enter your `start_date` - Optional. Start date to filter records when collecting data.
7. Enter your `end_date` - Optional. End date to filter records when collecting data.
8. Enter your `query` - Optional. Type your query to filter records when collecting data. 
9. Click **Set up source**.

## Supported sync modes

The Tenkft source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- |:-----------|
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

## Supported Streams

* [Users](https://10kft.github.io/10kft-api/#users)
* [Projects](https://10kft.github.io/10kft-api/#list-projects)
* [ProjectAssignments](https://10kft.github.io/10kft-api/#list-all-assignments)
* [BillRates](https://10kft.github.io/10kft-api/#bill-rates)

## Changelog

| Version | Date       | Pull Request                                              | Subject            |
|:--------|:-----------|:----------------------------------------------------------|:-------------------|
| 1.0.0   | 2023-03-09 | [23913](https://github.com/airbytehq/airbyte/pull/23913)  | New Source: Tenkft |
