# Coinmarketcap API

## Sync overview

This source can sync data from the [Coinmarketcap API](https://coinmarketcap.com/api/documentation/v1/). At present this connector only supports full refresh syncs meaning that each time you use the connector it will sync all available records from scratch. Please use cautiously if you expect your API to have a lot of records.

## This Source Supports the Following Streams

- [categories](https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyCategories)
- [listing](https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyListingsLatest)
- [quotes](https://coinmarketcap.com/api/documentation/v1/#operation/getV2CryptocurrencyQuotesLatest)
- [fiat](https://coinmarketcap.com/api/documentation/v1/#tag/fiat)
- [exchange](https://coinmarketcap.com/api/documentation/v1/#tag/exchange)

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | No                   |       |

### Performance considerations

Coinmarketcap APIs are under rate limits for the number of API calls allowed per API keys per second. If you reach a rate limit, API will return a 429 HTTP error code. See [here](https://coinmarketcap.com/api/documentation/v1/#section/Errors-and-Rate-Limits)

## Getting started

### Requirements

- [API token](https://coinmarketcap.com/api/documentation/v1/#section/Authentication)
- Data Type:
  - latest
  - historical

## Changelog

| Version | Date       | Pull Request                                              | Subject                                         |
| :------ | :--------- | :-------------------------------------------------------- | :---------------------------------------------- |
| 0.1.2   | 2024-05-13 | [38134](https://github.com/airbytehq/airbyte/pull/38134)  | Make connector compatabile with builder         |
| 0.1.1   | 2022-11-01 | [18790](https://github.com/airbytehq/airbyte/pull/18790)  | Correct coinmarket spec                         |
| 0.1.0   | 2022-10-29 | [18565](https://github.com/airbytehq/airbyte/pull/18565)  | 🎉 New Source: Coinmarketcap API [low-code CDK] |
