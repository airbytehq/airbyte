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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                                 | Subject         |
| :------ | :--------- | :----------------------------------------------------------- | :-------------- |
| 0.0.16 | 2026-07-21 | [82610](https://github.com/airbytehq/airbyte/pull/82610) | Update dependencies |
| 0.0.15 | 2026-07-14 | [82051](https://github.com/airbytehq/airbyte/pull/82051) | Update dependencies |
| 0.0.14 | 2026-06-30 | [81297](https://github.com/airbytehq/airbyte/pull/81297) | Update dependencies |
| 0.0.13 | 2026-06-23 | [80702](https://github.com/airbytehq/airbyte/pull/80702) | Update dependencies |
| 0.0.12 | 2026-06-16 | [80067](https://github.com/airbytehq/airbyte/pull/80067) | Update dependencies |
| 0.0.11 | 2026-06-09 | [79552](https://github.com/airbytehq/airbyte/pull/79552) | Update dependencies |
| 0.0.10 | 2026-06-02 | [78992](https://github.com/airbytehq/airbyte/pull/78992) | Update dependencies |
| 0.0.9 | 2026-04-28 | [77421](https://github.com/airbytehq/airbyte/pull/77421) | Update dependencies |
| 0.0.8 | 2026-04-21 | [76757](https://github.com/airbytehq/airbyte/pull/76757) | Update dependencies |
| 0.0.7 | 2026-03-31 | [75870](https://github.com/airbytehq/airbyte/pull/75870) | Update dependencies |
| 0.0.6 | 2026-03-24 | [75392](https://github.com/airbytehq/airbyte/pull/75392) | Update dependencies |
| 0.0.5 | 2026-02-24 | [73946](https://github.com/airbytehq/airbyte/pull/73946) | Update dependencies |
| 0.0.4 | 2026-02-17 | [72773](https://github.com/airbytehq/airbyte/pull/72773) | Update dependencies |
| 0.0.3 | 2026-01-20 | [72136](https://github.com/airbytehq/airbyte/pull/72136) | Update dependencies |
| 0.0.2 | 2026-01-14 | [71590](https://github.com/airbytehq/airbyte/pull/71590) | Update dependencies |
| 0.0.1 | 2026-01-10 | [71179](https://github.com/airbytehq/airbyte/pull/71179) | Initial release |

</details>
