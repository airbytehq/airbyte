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

| Version | Date      | Pull Request                                             | Subject                                                                         |
| :------ | :-------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.4.11 | 2025-01-25 | [52384](https://github.com/airbytehq/airbyte/pull/52384) | Update dependencies |
| 0.4.10 | 2025-01-18 | [52012](https://github.com/airbytehq/airbyte/pull/52012) | Update dependencies |
| 0.4.9 | 2025-01-11 | [51398](https://github.com/airbytehq/airbyte/pull/51398) | Update dependencies |
| 0.4.8 | 2024-12-28 | [50777](https://github.com/airbytehq/airbyte/pull/50777) | Update dependencies |
| 0.4.7 | 2024-12-21 | [50349](https://github.com/airbytehq/airbyte/pull/50349) | Update dependencies |
| 0.4.6 | 2024-12-14 | [49769](https://github.com/airbytehq/airbyte/pull/49769) | Update dependencies |
| 0.4.5 | 2024-12-12 | [49387](https://github.com/airbytehq/airbyte/pull/49387) | Update dependencies |
| 0.4.4 | 2024-12-11 | [48307](https://github.com/airbytehq/airbyte/pull/48307) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.4.3 | 2024-10-29 | [47887](https://github.com/airbytehq/airbyte/pull/47887) | Update dependencies |
| 0.4.2 | 2024-10-28 | [47503](https://github.com/airbytehq/airbyte/pull/47503) | Update dependencies |
| 0.4.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.4.0 | 2024-08-07 | [43368](https://github.com/airbytehq/airbyte/pull/43368) | Refactor connector to manifest-only format |
| 0.3.15 | 2024-08-03 | [43226](https://github.com/airbytehq/airbyte/pull/43226) | Update dependencies |
| 0.3.14 | 2024-07-27 | [42635](https://github.com/airbytehq/airbyte/pull/42635) | Update dependencies |
| 0.3.13 | 2024-07-20 | [42252](https://github.com/airbytehq/airbyte/pull/42252) | Update dependencies |
| 0.3.12 | 2024-07-13 | [41921](https://github.com/airbytehq/airbyte/pull/41921) | Update dependencies |
| 0.3.11 | 2024-07-10 | [41348](https://github.com/airbytehq/airbyte/pull/41348) | Update dependencies |
| 0.3.10 | 2024-07-09 | [41268](https://github.com/airbytehq/airbyte/pull/41268) | Update dependencies |
| 0.3.9 | 2024-07-06 | [40773](https://github.com/airbytehq/airbyte/pull/40773) | Update dependencies |
| 0.3.8 | 2024-06-26 | [40510](https://github.com/airbytehq/airbyte/pull/40510) | Update dependencies |
| 0.3.7 | 2024-06-22 | [39996](https://github.com/airbytehq/airbyte/pull/39996) | Update dependencies |
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
