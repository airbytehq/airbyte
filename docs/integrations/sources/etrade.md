# E*TRADE

This page contains the setup guide and reference information for the E\*TRADE source connector.

## Prerequisites

- An E\*TRADE brokerage account
- E\*TRADE API consumer key and consumer secret from the [E\*TRADE Developer Portal](https://developer.etrade.com)
- OAuth 1.0a access token and token secret obtained through the E\*TRADE authorization flow

## Setup guide

### Step 1: Obtain API credentials

1. Visit the [E\*TRADE Developer Portal](https://developer.etrade.com) and sign in.
2. Register a new application to obtain your **Consumer Key** and **Consumer Secret**.
3. Complete the OAuth 1.0a authorization flow to obtain an **OAuth Token** and **OAuth Token Secret**.

### Step 2: Set up the E\*TRADE connector in Airbyte

1. Log into your Airbyte account.
2. In the left navigation bar, click **Sources**, then click **+ New source** in the top-right corner.
3. Find and select **E\*TRADE** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter your **Consumer Key**, **Consumer Secret**, **OAuth Token**, and **OAuth Token Secret**.
6. Optionally enable **Use Sandbox** to test with mock data.
7. Optionally specify **Account ID Keys** to sync only specific accounts.
8. Optionally set a **Start Date** for incremental streams.
9. Click **Set up source** and wait for the connection test to complete.

## Supported sync modes

The E\*TRADE source connector supports the following sync modes:

| Feature                   | Supported? |
| :------------------------ | :--------- |
| Full Refresh Sync         | Yes        |
| Incremental - Append Sync | Yes        |
| Namespaces                | No         |

## Supported streams

This source is capable of syncing the following streams:

| Stream              | Sync Mode             | Description                                      |
| :------------------ | :-------------------- | :----------------------------------------------- |
| accounts            | Full Refresh          | Lists all E\*TRADE accounts                      |
| portfolio           | Full Refresh          | Current holdings/positions per account            |
| balances            | Full Refresh          | Account balances, buying power, margin details    |
| orders              | Incremental           | Orders per account with status and fill details   |
| transactions        | Incremental           | Account transactions with date range filtering    |
| transaction_details | Full Refresh          | Detailed information for each transaction         |
| quotes              | Full Refresh          | Market quotes for symbols in user's portfolio     |
| product_lookup      | Full Refresh          | Security lookup results                           |
| alerts              | Full Refresh          | Account and stock alerts                          |
| alert_details       | Full Refresh          | Detailed alert information                        |

## Authentication

This connector uses **OAuth 1.0a** authentication. E\*TRADE access tokens expire at midnight US Eastern time daily. If syncs fail with authentication errors, you may need to renew your access tokens through the E\*TRADE OAuth flow.

## Limitations and troubleshooting

- **Token expiration**: E\*TRADE OAuth tokens expire at midnight US Eastern time and must be renewed daily. Tokens not used for 2+ hours also become inactive.
- **Rate limits**: The E\*TRADE API does not publish explicit rate limits. The connector uses conservative request pacing.
- **Transaction history**: Transaction data is available for up to 2 years.
- **Quotes**: The quotes stream retrieves quotes for symbols found in the user's portfolio. Real-time data requires a signed market data agreement; otherwise data is delayed.
- **Sandbox**: The sandbox environment returns mock data and can be used for testing without a funded account.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject          |
| :------ | :--------- | :----------- | :--------------- |
| 0.1.0   | 2026-04-16 | TBD          | Initial release  |

</details>
