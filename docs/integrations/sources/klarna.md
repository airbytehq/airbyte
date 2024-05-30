# Klarna

This page contains the setup guide and reference information for the Klarna source connector.

## Prerequisites

The [Klarna Settlements API](https://developers.klarna.com/api/#settlements-api) is used to get the payouts and transactions for a Klarna account.

## Setup guide

### Step 1: Set up Klarna

In order to get an `Username (UID)` and `Password` please go to [this](https://docs.klarna.com/) page here you should find **Merchant Portal** button. Using this button you could log in to your production / playground in proper region. After registration / login you may find and create `Username (UID)` and `Password` in settings tab.

:::note

Klarna Source Connector does not support OAuth at this time due to limitations outside of control.

:::

## Step 2: Set up the Klarna connector in Airbyte

### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard
2. Set the name for your source
3. Choose if your account is sandbox
4. Enter your username
5. Enter your password
6. Enter the date you want your sync to start from
7. Click **Set up source**

## Supported sync modes

The Klarna source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | No         |

## Supported Streams

This Source is capable of syncing the following Klarna Settlements Streams:

- [Payouts](https://developers.klarna.com/api/#settlements-api-get-all-payouts)
- [Transactions](https://developers.klarna.com/api/#settlements-api-get-transactions)

## Performance considerations

Klarna API has [rate limiting](https://developers.klarna.com/api/#api-rate-limiting)

**Production environments**: the API rate limit is 20 create-sessions per second on average measured over a 1-minute period. For the other operations, the API limit is 200 requests per second on average, measured over a 1 minute period
**Playground environments**: the API rate limit is one quarter (1/4th) of the rate limits of production environments.

Connector will handle an issue with rate limiting as Klarna returns 429 status code when limits are reached

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.4   | 2024-04-19 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | Updating to 0.80.0 CDK                                                          |
| 0.2.3   | 2024-04-18 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | Manage dependencies with Poetry.                                                |
| 0.2.2   | 2024-04-15 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1   | 2024-04-12 | [37182](https://github.com/airbytehq/airbyte/pull/37182) | schema descriptions                                                             |
| 0.2.0   | 2023-10-23 | [31003](https://github.com/airbytehq/airbyte/pull/31003) | Migrate to low-code                                                             |
| 0.1.0   | 2022-10-24 | [18385](https://github.com/airbytehq/airbyte/pull/18385) | Klarna Settlements Payout and Transactions API                                  |
