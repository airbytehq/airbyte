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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.6 | 2024-06-04 | [39054](https://github.com/airbytehq/airbyte/pull/39054) | [autopull] Upgrade base image to v1.2.1 |
| 0.3.5 | 2024-05-20 | [38228](https://github.com/airbytehq/airbyte/pull/38228) | Make compatible with builder |
| 0.3.4 | 2024-04-19 | [37270](https://github.com/airbytehq/airbyte/pull/37270) | Updating to 0.80.0 CDK |
| 0.3.3 | 2024-04-18 | [37270](https://github.com/airbytehq/airbyte/pull/37270) | Manage dependencies with Poetry. |
| 0.3.2 | 2024-04-15 | [37270](https://github.com/airbytehq/airbyte/pull/37270) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.3.1 | 2024-04-12 | [37270](https://github.com/airbytehq/airbyte/pull/37270) | schema descriptions |
| 0.3.0 | 2023-10-25 | [31002](https://github.com/airbytehq/airbyte/pull/31002) | Migrate to low-code framework |
| 0.2.0 | 2023-10-23 | [31745](https://github.com/airbytehq/airbyte/pull/31745) | Fix schemas |
| 0.1.0 | 2022-06-22 | [13617](https://github.com/airbytehq/airbyte/pull/13617) | Initial release |

</details>
