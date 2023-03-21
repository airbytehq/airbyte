# CoinMarketCap API

This page guides you through the process of setting up the CoinMarketCap source connector.

## Prerequisites

- [API token](https://coinmarketcap.com/api/documentation/v1/#section/Authentication)

:::note

At least `HOBBYIST` subscription level is required to access historical data.

:::

## Setup guide

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **CoinMarketCap** from the **Source type** dropdown.
4. Enter a name for the CoinMarketCap connector.
5. Enter API Key.
6. Select Data type.
7. Enter Symbols for Cryptocurrencies to sync or leave empty to sync all (Optional).


#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **CoinMarketCap** from the Source type dropdown.
4. Enter a name for the CoinMarketCap connector.
5. Enter API Key.
6. Select Data type.
7. Enter Symbols for Cryptocurrencies to sync or leave empty to sync all (Optional).

## Supported sync modes

The CoinMarketCap API source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)

## Supported Streams

- [categories](https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyCategories)
- [listing](https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest)
- [quotes](https://coinmarketcap.com/api/documentation/v1/#operation/getV2CryptocurrencyQuotesLatest)
- [fiat](https://coinmarketcap.com/api/documentation/v1/#tag/fiat)
- [exchange](https://coinmarketcap.com/api/documentation/v1/#tag/exchange)

## Performance considerations

Coinmarketcap APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://coinmarketcap.com/api/documentation/v1/#section/Errors-and-Rate-Limits)

## Data type mapping

| Integration Type | Airbyte Type | Notes |
|:-----------------|:-------------|:------|
| `string`         | `string`     |       |
| `integer`        | `integer`    |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

## Changelog

| Version | Date       | Pull Request                                              | Subject                                         |
|:--------|:-----------|:----------------------------------------------------------|:------------------------------------------------|
| 0.1.2   | 2023-03-21 | [#24276](https://github.com/airbytehq/airbyte/pull/24276) | Update to latest CDK                            |
| 0.1.1   | 2022-11-01 | [#18790](https://github.com/airbytehq/airbyte/pull/18790) | Correct coinmarket spec                         |
| 0.1.0   | 2022-10-29 | [#18565](https://github.com/airbytehq/airbyte/pull/18565) | 🎉 New Source: Coinmarketcap API [low-code CDK] |
