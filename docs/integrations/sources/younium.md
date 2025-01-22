# Younium

This page contains the setup guide and reference information for the Younium source connector.

## Prerequisites

This Younium source uses the [Younium API](https://developer.younium.com/).

## Setup guide

### Step 1: Set up Younium

#### For Airbyte OSS:

1. Navigate to the Airbyte Open Source dashboard
2. Enter a name for your source
3. Enter your Younium `username`
4. Enter your Younium `password`
5. Enter your Younium `legal_entity`. You can find the legal entity name in your account setting if you log in to the [Younium web platform](https://app.younium.com/)
6. Click **Set up source**

## Supported sync modes

The Younium source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                       | Supported? |
| :---------------------------- | :--------- |
| Full Refresh Sync             | Yes        |
| Incremental - Append Sync     | No         |
| Replicate Incremental Deletes | No         |
| SSL connection                | Yes        |
| Namespaces                    | No         |

## Supported Streams

- [Accounts](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Accounts)
- [Bookings](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Bookings)
- [Subscriptions](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Subscriptions)
- [Products](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Products)
- [Invoices](https://developer.younium.com/api-details#api=Production_API2-0&operation=Get-Invoices)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                    |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------- |
| 0.4.5 | 2025-01-18 | [51956](https://github.com/airbytehq/airbyte/pull/51956) | Update dependencies |
| 0.4.4 | 2025-01-11 | [51416](https://github.com/airbytehq/airbyte/pull/51416) | Update dependencies |
| 0.4.3 | 2024-12-28 | [50781](https://github.com/airbytehq/airbyte/pull/50781) | Update dependencies |
| 0.4.2 | 2024-12-21 | [49787](https://github.com/airbytehq/airbyte/pull/49787) | Update dependencies |
| 0.4.1 | 2024-12-12 | [46856](https://github.com/airbytehq/airbyte/pull/46856) | Update dependencies |
| 0.4.0 | 2024-10-23 | [47281](https://github.com/airbytehq/airbyte/pull/47281) | Migrate to Manifest-only |
| 0.3.22 | 2024-10-05 | [46432](https://github.com/airbytehq/airbyte/pull/46432) | Update dependencies |
| 0.3.21 | 2024-09-28 | [46176](https://github.com/airbytehq/airbyte/pull/46176) | Update dependencies |
| 0.3.20 | 2024-09-21 | [45807](https://github.com/airbytehq/airbyte/pull/45807) | Update dependencies |
| 0.3.19 | 2024-09-14 | [45475](https://github.com/airbytehq/airbyte/pull/45475) | Update dependencies |
| 0.3.18 | 2024-09-07 | [45276](https://github.com/airbytehq/airbyte/pull/45276) | Update dependencies |
| 0.3.17 | 2024-08-31 | [45054](https://github.com/airbytehq/airbyte/pull/45054) | Update dependencies |
| 0.3.16 | 2024-08-24 | [44711](https://github.com/airbytehq/airbyte/pull/44711) | Update dependencies |
| 0.3.15 | 2024-08-17 | [44362](https://github.com/airbytehq/airbyte/pull/44362) | Update dependencies |
| 0.3.14 | 2024-08-12 | [43925](https://github.com/airbytehq/airbyte/pull/43925) | Update dependencies |
| 0.3.13 | 2024-08-10 | [43475](https://github.com/airbytehq/airbyte/pull/43475) | Update dependencies |
| 0.3.12 | 2024-08-03 | [43060](https://github.com/airbytehq/airbyte/pull/43060) | Update dependencies |
| 0.3.11 | 2024-07-27 | [42712](https://github.com/airbytehq/airbyte/pull/42712) | Update dependencies |
| 0.3.10 | 2024-07-20 | [42158](https://github.com/airbytehq/airbyte/pull/42158) | Update dependencies |
| 0.3.9 | 2024-07-13 | [41716](https://github.com/airbytehq/airbyte/pull/41716) | Update dependencies |
| 0.3.8 | 2024-07-10 | [41281](https://github.com/airbytehq/airbyte/pull/41281) | Update dependencies |
| 0.3.7 | 2024-07-06 | [40769](https://github.com/airbytehq/airbyte/pull/40769) | Update dependencies |
| 0.3.6 | 2024-06-25 | [40263](https://github.com/airbytehq/airbyte/pull/40263) | Update dependencies |
| 0.3.5 | 2024-06-22 | [39966](https://github.com/airbytehq/airbyte/pull/39966) | Update dependencies |
| 0.3.4 | 2024-06-06 | [39213](https://github.com/airbytehq/airbyte/pull/39213) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.3 | 2024-05-20 | [38407](https://github.com/airbytehq/airbyte/pull/38407) | [autopull] base image + poetry + up_to_date |
| 0.3.2 | 2024-04-19 | [37298](https://github.com/airbytehq/airbyte/pull/37298) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.3.1 | 2024-04-12 | [37298](https://github.com/airbytehq/airbyte/pull/37298) | schema descriptions |
| 0.3.0 | 2023-10-25 | [31690](https://github.com/airbytehq/airbyte/pull/31690) | Migrate to low-code framework |
| 0.2.0 | 2023-03-29 | [24655](https://github.com/airbytehq/airbyte/pull/24655) | Source Younium: Adding Booking and Account streams |
| 0.1.0 | 2022-11-09 | [18758](https://github.com/airbytehq/airbyte/pull/18758) | 🎉 New Source: Younium [python cdk] |

</details>
