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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                              | Subject                                         |
| :------ | :--------- | :-------------------------------------------------------- | :---------------------------------------------- |
| 0.2.3 | 2025-01-18 | [51643](https://github.com/airbytehq/airbyte/pull/51643) | Update dependencies |
| 0.2.2 | 2025-01-11 | [47781](https://github.com/airbytehq/airbyte/pull/47781) | Update dependencies |
| 0.2.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 0.2.0 | 2024-08-15 | [44163](https://github.com/airbytehq/airbyte/pull/44163) | Refactor connector to manifest-only format |
| 0.1.14 | 2024-08-12 | [43905](https://github.com/airbytehq/airbyte/pull/43905) | Update dependencies |
| 0.1.13 | 2024-08-10 | [43684](https://github.com/airbytehq/airbyte/pull/43684) | Update dependencies |
| 0.1.12 | 2024-08-03 | [43227](https://github.com/airbytehq/airbyte/pull/43227) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42766](https://github.com/airbytehq/airbyte/pull/42766) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42332](https://github.com/airbytehq/airbyte/pull/42332) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41856](https://github.com/airbytehq/airbyte/pull/41856) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41442](https://github.com/airbytehq/airbyte/pull/41442) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41141](https://github.com/airbytehq/airbyte/pull/41141) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40961](https://github.com/airbytehq/airbyte/pull/40961) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40427](https://github.com/airbytehq/airbyte/pull/40427) | Update dependencies |
| 0.1.4 | 2024-06-21 | [39942](https://github.com/airbytehq/airbyte/pull/39942) | Update dependencies |
| 0.1.3 | 2024-06-06 | [39161](https://github.com/airbytehq/airbyte/pull/39161) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.2 | 2024-05-13 | [38134](https://github.com/airbytehq/airbyte/pull/38134) | Make connector compatabile with builder |
| 0.1.1 | 2022-11-01 | [18790](https://github.com/airbytehq/airbyte/pull/18790) | Correct coinmarket spec |
| 0.1.0 | 2022-10-29 | [18565](https://github.com/airbytehq/airbyte/pull/18565) | 🎉 New Source: Coinmarketcap API [low-code CDK] |

</details>
