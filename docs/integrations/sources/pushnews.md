# Pushnews

This page contains the setup guide and reference information for the [Pushnews](https://docs.pushnews.eu/) source connector.

## This Source Supports the Following Streams

* sites
* site configuration
* notifications
* push on site
* posh on site events

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |

## Setup guide

### Prerequisites

* `Access Key`. Go to [api page](https://app.pushnews.eu/account/api) and get  API key.

### Step 1: Set up Pushnews connection

* Pass API key (Example: 12345)
* Available params (If specific info is needed)
  * start_date: UTC date  in the format 2020-10-01. Any data before this date will not be replicated. If omitted, defaults to 2017-11-01.
  * status: Filter events by status. 'all', 'active' or 'inactive' are possible values. The default is 'all'.
  * force_update_stats: Enable to force statistics update, reduce performance when activated. The default is 'false'.

## Step 2: Set up the Pushnews connector in Airbyte

### For Airbyte Cloud

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Pushnews connector and select **Pushnews** from the Source type dropdown.
4. Enter your `api_key`.
5. Enter the params configuration if needed. Supported params are: start_date, status, force_update_stats
6. Click **Set up source**.

### For Airbyte OSS

1. Navigate to the Airbyte Open Source dashboard.
2. Set the name for your source.
4. Enter your `api_key`.
5. Enter the params configuration if needed. Supported params are: start_date, status, force_update_stats
6. Click **Set up source**.

## Supported sync modes

The Pushnews source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental Sync              | Yes        |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

* sites
* site configuration
* notifications
* push on site
* posh on site events

## API method example

GET <https://api.pushnews.eu/v2/sites>

## Performance considerations

Pushnews [API reference](https://docs.pushnews.com.br/) has v2 at present and v1 as depricated. The connector as default uses v2.
