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
| 0.3.4 | 2024-06-06 | [39213](https://github.com/airbytehq/airbyte/pull/39213) | [autopull] Upgrade base image to v1.2.2 |
| 0.3.3 | 2024-05-20 | [38407](https://github.com/airbytehq/airbyte/pull/38407) | [autopull] base image + poetry + up_to_date |
| 0.3.2 | 2024-04-19 | [37298](https://github.com/airbytehq/airbyte/pull/37298) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.3.1 | 2024-04-12 | [37298](https://github.com/airbytehq/airbyte/pull/37298) | schema descriptions |
| 0.3.0 | 2023-10-25 | [31690](https://github.com/airbytehq/airbyte/pull/31690) | Migrate to low-code framework |
| 0.2.0 | 2023-03-29 | [24655](https://github.com/airbytehq/airbyte/pull/24655) | Source Younium: Adding Booking and Account streams |
| 0.1.0 | 2022-11-09 | [18758](https://github.com/airbytehq/airbyte/pull/18758) | 🎉 New Source: Younium [python cdk] |

</details>
