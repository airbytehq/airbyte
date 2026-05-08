# Customer.io

## Overview

<HideInUI>

This page contains the setup guide and reference information for the [Customer.io](https://customer.io/) source connector.

</HideInUI>

The Customer.io source connector uses the [Customer.io App API](https://docs.customer.io/integrations/api/app/) to replicate campaign, campaign action, and newsletter metadata from a Customer.io workspace.

## Prerequisites

- A Customer.io account with access to the workspace you want to sync.
- A Customer.io App API key. Track API keys are not supported.
- Permission to manage API credentials in Customer.io. Customer.io requires the Account Admin role or the account-level **Manage API credentials** permission to access API credentials.
- Your Customer.io workspace region: `US` or `EU`.

If your Customer.io account restricts API access by IP address, ensure that the environment running Airbyte is allowed to access the Customer.io App API.

## Setup guide

### Step 1: Create a Customer.io app API key

1. Log in to Customer.io.
2. Go to **Account Settings > API Credentials**.
3. Create or select API credentials for the workspace you want to sync.
4. Copy the **App API Key** and store it securely. Customer.io only shows App API keys once when you create them.

For more information, see Customer.io's [Manage your API credentials](https://docs.customer.io/accounts-and-workspaces/managing-credentials/) documentation.

### Step 2: Set up the Customer.io source in Airbyte

1. Enter a **Name** for the source.

<FieldAnchor field="app_api_key">

1. Enter your **Customer.io App API Key**.

</FieldAnchor>

<FieldAnchor field="region">

1. For **Region**, select the region where your Customer.io workspace is hosted. Select **EU** for workspaces that use `https://api-eu.customer.io`. Select **US** for workspaces that use `https://api.customer.io`.

</FieldAnchor>

<FieldAnchor field="start_date">

1. For **Start Date**, optionally enter a UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`. For incremental syncs, records with an `updated` timestamp before this date are filtered out by the connector. Leave this field blank to sync all available records.

</FieldAnchor>

1. Click **Set up source** and wait for the connection test to complete.

## Supported sync modes

The Customer.io source connector supports the following sync modes:

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |

## Supported streams

| Stream              | Endpoint                              | Sync mode   | Primary key | Cursor field |
| :------------------ | :------------------------------------ | :---------- | :---------- | :----------- |
| `campaigns`         | `/v1/campaigns`                       | Incremental | `id`        | `updated`    |
| `campaigns_actions` | `/v1/campaigns/{campaign_id}/actions` | Incremental | `id`        | `updated`    |
| `newsletters`       | `/v1/newsletters`                     | Incremental | `id`        | `updated`    |

The `campaigns_actions` stream is a child stream of `campaigns`. The connector first reads campaign IDs, then requests actions for each campaign.

For incremental syncs, the connector uses the `updated` field returned by Customer.io. Customer.io returns `updated` as a Unix timestamp in seconds. The connector applies the incremental filter client-side, so syncs can still make API requests for records that are filtered out before records are emitted.

## Performance considerations

Customer.io hosts App API endpoints in the United States at `https://api.customer.io` and in the EU at `https://api-eu.customer.io`. Select the region that matches your Customer.io workspace.

Most Customer.io App API endpoints are limited to 10 requests per second. The `campaigns_actions` stream can make many requests because it requests actions separately for each campaign. Customer.io returns up to 10 actions per campaign-actions page. The newsletters stream requests up to 100 newsletters per page.

## Reference

| Field         | Type   | Required | Description                                                                                                                            |
| :------------ | :----- | :------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| `app_api_key` | String | Yes      | Customer.io App API key used as a bearer token.                                                                                        |
| `region`      | String | No       | Customer.io workspace region. Valid values are `US` and `EU`. The default is `US`.                                                     |
| `start_date`  | String | No       | UTC date and time in `YYYY-MM-DDTHH:MM:SSZ` format. Incremental syncs filter out records with an `updated` timestamp before this date. |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                   | Subject                                                                                                                                             |
| :------ | :--------- | :------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0.4.1   | 2026-05-08 | [77895](https://github.com/airbytehq/airbyte/pull/77895)       | Align the manifest runtime image with the CDK 7.18.1 behavior used by Customer.io tests                                                             |
| 0.4.0   | 2026-05-08 | [77819](https://github.com/airbytehq/airbyte/pull/77819)       | Add pagination on `campaigns_actions` and `newsletters`, client-side incremental sync on the `updated` cursor, and a configurable `region` selector |
| 0.3.19  | 2025-08-20 | [65113](https://github.com/airbytehq/airbyte/pull/65113)       | Update logo                                                                                                                                         |
| 0.3.18  | 2025-05-10 | [60049](https://github.com/airbytehq/airbyte/pull/60049)       | Update dependencies                                                                                                                                 |
| 0.3.17  | 2025-05-03 | [58875](https://github.com/airbytehq/airbyte/pull/58875)       | Update dependencies                                                                                                                                 |
| 0.3.16  | 2025-04-19 | [57766](https://github.com/airbytehq/airbyte/pull/57766)       | Update dependencies                                                                                                                                 |
| 0.3.15  | 2025-04-05 | [57225](https://github.com/airbytehq/airbyte/pull/57225)       | Update dependencies                                                                                                                                 |
| 0.3.14  | 2025-03-29 | [56546](https://github.com/airbytehq/airbyte/pull/56546)       | Update dependencies                                                                                                                                 |
| 0.3.13  | 2025-03-22 | [55918](https://github.com/airbytehq/airbyte/pull/55918)       | Update dependencies                                                                                                                                 |
| 0.3.12  | 2025-03-08 | [55311](https://github.com/airbytehq/airbyte/pull/55311)       | Update dependencies                                                                                                                                 |
| 0.3.11  | 2025-03-01 | [54942](https://github.com/airbytehq/airbyte/pull/54942)       | Update dependencies                                                                                                                                 |
| 0.3.10  | 2025-02-22 | [54374](https://github.com/airbytehq/airbyte/pull/54374)       | Update dependencies                                                                                                                                 |
| 0.3.9   | 2025-02-15 | [51670](https://github.com/airbytehq/airbyte/pull/51670)       | Update dependencies                                                                                                                                 |
| 0.3.8   | 2025-01-11 | [51062](https://github.com/airbytehq/airbyte/pull/51062)       | Update dependencies                                                                                                                                 |
| 0.3.7   | 2025-01-04 | [50582](https://github.com/airbytehq/airbyte/pull/50582)       | Update dependencies                                                                                                                                 |
| 0.3.6   | 2024-12-21 | [49999](https://github.com/airbytehq/airbyte/pull/49999)       | Update dependencies                                                                                                                                 |
| 0.3.5   | 2024-12-14 | [49490](https://github.com/airbytehq/airbyte/pull/49490)       | Update dependencies                                                                                                                                 |
| 0.3.4   | 2024-12-12 | [48923](https://github.com/airbytehq/airbyte/pull/48923)       | Update dependencies                                                                                                                                 |
| 0.3.3   | 2024-11-04 | [48225](https://github.com/airbytehq/airbyte/pull/48225)       | Update dependencies                                                                                                                                 |
| 0.3.2   | 2024-10-28 | [47464](https://github.com/airbytehq/airbyte/pull/47464)       | Update dependencies                                                                                                                                 |
| 0.3.1   | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196)       | Bump source-declarative-manifest version                                                                                                            |
| 0.3.0   | 2024-08-15 | [44158](https://github.com/airbytehq/airbyte/pull/44158)       | Refactor connector to manifest-only format                                                                                                          |
| 0.2.15  | 2024-08-12 | [43889](https://github.com/airbytehq/airbyte/pull/43889)       | Update dependencies                                                                                                                                 |
| 0.2.14  | 2024-08-10 | [43513](https://github.com/airbytehq/airbyte/pull/43513)       | Update dependencies                                                                                                                                 |
| 0.2.13  | 2024-08-03 | [43185](https://github.com/airbytehq/airbyte/pull/43185)       | Update dependencies                                                                                                                                 |
| 0.2.12  | 2024-07-27 | [42631](https://github.com/airbytehq/airbyte/pull/42631)       | Update dependencies                                                                                                                                 |
| 0.2.11  | 2024-07-20 | [42219](https://github.com/airbytehq/airbyte/pull/42219)       | Update dependencies                                                                                                                                 |
| 0.2.10  | 2024-07-13 | [41808](https://github.com/airbytehq/airbyte/pull/41808)       | Update dependencies                                                                                                                                 |
| 0.2.9   | 2024-07-10 | [41389](https://github.com/airbytehq/airbyte/pull/41389)       | Update dependencies                                                                                                                                 |
| 0.2.8   | 2024-07-09 | [41225](https://github.com/airbytehq/airbyte/pull/41225)       | Update dependencies                                                                                                                                 |
| 0.2.7   | 2024-07-06 | [40883](https://github.com/airbytehq/airbyte/pull/40883)       | Update dependencies                                                                                                                                 |
| 0.2.6   | 2024-06-29 | [40624](https://github.com/airbytehq/airbyte/pull/40624)       | Update dependencies                                                                                                                                 |
| 0.2.5   | 2024-06-27 | [38318](https://github.com/airbytehq/airbyte/pull/38318)       | Make compatibility with builder                                                                                                                     |
| 0.2.4   | 2024-06-25 | [40369](https://github.com/airbytehq/airbyte/pull/40369)       | Update dependencies                                                                                                                                 |
| 0.2.3   | 2024-06-22 | [39953](https://github.com/airbytehq/airbyte/pull/39953)       | Update dependencies                                                                                                                                 |
| 0.2.2   | 2024-06-04 | [38980](https://github.com/airbytehq/airbyte/pull/38980)       | [auto-pull] Upgrade base image to v1.2.1                                                                                                            |
| 0.2.1   | 2024-05-31 | [38812](https://github.com/airbytehq/airbyte/pull/38812)       | [auto-pull] Migrate to base image and poetry                                                                                                        |
| 0.2.0   | 2021-11-09 | [29385](https://github.com/airbytehq/airbyte/pull/29385)       | Migrate TS CDK to Low code                                                                                                                          |
| 0.1.23  | 2021-11-09 | [126](https://github.com/faros-ai/airbyte-connectors/pull/126) | Add Customer.io source                                                                                                                              |

</details>
