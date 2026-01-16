# Stigg

This page contains the setup guide and reference information for the Stigg source connector.

[Stigg](https://stigg.io) is a pricing and packaging infrastructure platform that helps SaaS companies manage their monetization strategy. It provides tools for defining pricing plans, managing customer subscriptions, tracking feature entitlements, and metering usage.

## Prerequisites

- A Stigg account
- A Stigg Server API Key

## Setup guide

### Step 1: Obtain your Stigg API Key

1. Log in to your [Stigg dashboard](https://app.stigg.io)
2. Navigate to **Settings > Account > Environments**
3. Copy the **Server API key** for the relevant environment

### Step 2: Set up the Stigg connector in Airbyte

1. Log in to your Airbyte Cloud account or navigate to your Airbyte Open Source dashboard
2. In the left navigation bar, click **Sources**, then click **+ New source** in the top-right corner
3. Find and select **Stigg** from the list of available sources
4. Enter a name for your Stigg source
5. Enter your Server API Key
6. Click **Set up source**

## Supported sync modes

The Stigg source connector supports the following sync modes:

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Supported streams

- [Customers](https://docs.stigg.io/api-and-sdks/integration/backend/graphql#getting-customer-data) - Returns all customers in your Stigg account, including their billing information, payment method status, and subscription counts
- [Subscriptions](https://docs.stigg.io/api-and-sdks/integration/backend/graphql#getting-a-subscription) - Returns all subscriptions in your Stigg account, including status, billing period, and trial information

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                 | Subject         |
| :------ | :--------- | :----------------------------------------------------------- | :-------------- |
| 0.0.2 | 2026-01-14 | [71590](https://github.com/airbytehq/airbyte/pull/71590) | Update dependencies |
| 0.0.1 | 2026-01-10 | [71179](https://github.com/airbytehq/airbyte/pull/71179) | Initial release |

</details>
