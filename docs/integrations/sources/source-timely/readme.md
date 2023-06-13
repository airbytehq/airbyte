# Timely

This page contains the setup guide and reference information for the Timely source connector.

## Prerequisites

1. Please follow these [steps](https://dev.timelyapp.com/#authorization) to obtain `Bearer_token` for your account.
2. Login into your `https://app.timelyapp.com` portal, fetch the `account-id` present in the URL (example: URL `https://app.timelyapp.com/12345/calendar` and account-id `12345`).
3. Get a start-date to your events. Dateformat `YYYY-MM-DD`.

## Setup guide
## Step 1: Set up the Timely connector in Airbyte

### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+new source**.
3. On the Set up the source page, enter the name for the Timely connector and select **Timely** from the Source type dropdown.
4. Enter your `Bearer_token`, `account-id`, and `start-date`.
5. Select `Authenticate your account`.
6. Click **Set up source**.

## Supported sync modes

The Timely source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Changelog

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 0.1.0   | 2022-06-22 | [13617](https://github.com/airbytehq/airbyte/pull/13617) | Initial release |
