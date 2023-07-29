# UptimeRobot

This is a setup guide for the UptimeRobot source connector which ingests data from the monitoring service.

## Prerequisites

An API key is required to get hold of data from API. See the [account settings page](https://uptimerobot.com/dashboard.php#mySettings) to obtain a key.

## Setup guide

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **UptimeRobot** from the Source type dropdown.
4. Enter a name for your source.
5. For the **api_key**, enter UptimeRobot api_key.
7. Enter **Start date** in YYYY-MM-DD format. The data added on and after this date will be replicated.
8. Click **Set up source**.

## Supported sync modes

The source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Changelog

| Version | Date       | Pull Request                                             | Description      |
| ------- | ---------- | -------------------------------------------------------- | ---------------- |
| 0.0.1   | 2023-07-30 | [28844](https://github.com/airbytehq/airbyte/pull/28844) | Initial version. |
