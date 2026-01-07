# Stigg

This page contains the setup guide and reference information for the Stigg source connector.

## Prerequisites

- A Stigg account
- A Stigg Server API Key

## Setup guide

### Step 1: Obtain your Stigg API Key

1. Log in to your [Stigg dashboard](https://app.stigg.io)
2. Navigate to Settings > API Keys
3. Copy your Server API Key

### Step 2: Set up the Stigg connector in Airbyte

1. Log in to your Airbyte Cloud account or navigate to your Airbyte Open Source dashboard
2. In the left navigation bar, click Sources, then click + New source in the top-right corner
3. Find and select Stigg from the list of available sources
4. Enter a name for your Stigg source
5. Enter your Server API Key
6. Optionally, enter a Customer ID to filter subscriptions
7. Optionally, enter a Resource ID to filter subscriptions
8. Click Set up source

## Supported sync modes

The Stigg source connector supports the following sync modes:

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | No         |

## Supported streams

- [Customers](https://api-docs.stigg.io/how-to-use-stigg-api) - Returns all customers in your Stigg account
- [Subscriptions](https://api-docs.stigg.io/how-to-use-stigg-api) - Returns active subscriptions (optionally filtered by customer or resource)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject         |
| :------ | :--------- | :----------- | :-------------- |
| 0.0.1   | 2026-01-07 | TBD          | Initial release |

</details>
