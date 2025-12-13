# Twelve Data
Twelve data can be used to access the data of world financial markets including stocks, forex, ETFs, indices, and cryptocurrencies.
This connector has various streams including but not limited to Stocks , Forex Pairs , Crypto Currencies , Time Series and Techical Indicators

Docs : https://twelvedata.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `country` | `string` | Country. Where instrument is traded |  |
| `exchange` | `string` | Exchange. Where instrument is traded |  |
| `symbol` | `string` | Symbol. Ticker of the instrument |  |
| `interval` | `enum` | Interval. Between two consecutive points in time series Supports: 1min, 5min, 15min, 30min, 45min, 1h, 2h, 4h, 1day, 1week, 1month |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Stocks | symbol | No pagination | ✅ |  ❌  |
| Forex Pairs | symbol | No pagination | ✅ |  ❌  |
| Crypto Currencies |  | No pagination | ✅ |  ❌  |
| Funds | symbol | No pagination | ✅ |  ❌  |
| Bonds | symbol | No pagination | ✅ |  ❌  |
| ETFs | symbol | No pagination | ✅ |  ❌  |
| Commodities | symbol | No pagination | ✅ |  ❌  |
| Exchanges | code | No pagination | ✅ |  ❌  |
| Cryptocurrency Exchanges |  | No pagination | ✅ |  ❌  |
| Market State | code | No pagination | ✅ |  ❌  |
| Instrument Type |  | No pagination | ✅ |  ❌  |
| Countries |  | No pagination | ✅ |  ❌  |
| Technical Indicators |  | No pagination | ✅ |  ❌  |
| Time Series |  | No pagination | ✅ |  ❌  |
| Exchange Rate |  | No pagination | ✅ |  ❌  |
| Quote |  | No pagination | ✅ |  ❌  |
| Price |  | No pagination | ✅ |  ❌  |
| EOD Price |  | No pagination | ✅ |  ❌  |
| Mutual Funds | symbol | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.42 | 2025-12-09 | [70788](https://github.com/airbytehq/airbyte/pull/70788) | Update dependencies |
| 0.0.41 | 2025-11-25 | [69877](https://github.com/airbytehq/airbyte/pull/69877) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69709](https://github.com/airbytehq/airbyte/pull/69709) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68885](https://github.com/airbytehq/airbyte/pull/68885) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68557](https://github.com/airbytehq/airbyte/pull/68557) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67866](https://github.com/airbytehq/airbyte/pull/67866) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67508](https://github.com/airbytehq/airbyte/pull/67508) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66836](https://github.com/airbytehq/airbyte/pull/66836) | Update dependencies |
| 0.0.34 | 2025-09-23 | [66605](https://github.com/airbytehq/airbyte/pull/66605) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65740](https://github.com/airbytehq/airbyte/pull/65740) | Update dependencies |
| 0.0.32 | 2025-08-24 | [65463](https://github.com/airbytehq/airbyte/pull/65463) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64841](https://github.com/airbytehq/airbyte/pull/64841) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64397](https://github.com/airbytehq/airbyte/pull/64397) | Update dependencies |
| 0.0.29 | 2025-07-26 | [64085](https://github.com/airbytehq/airbyte/pull/64085) | Update dependencies |
| 0.0.28 | 2025-07-20 | [63686](https://github.com/airbytehq/airbyte/pull/63686) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63197](https://github.com/airbytehq/airbyte/pull/63197) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62711](https://github.com/airbytehq/airbyte/pull/62711) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62248](https://github.com/airbytehq/airbyte/pull/62248) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61771](https://github.com/airbytehq/airbyte/pull/61771) | Update dependencies |
| 0.0.23 | 2025-06-15 | [60463](https://github.com/airbytehq/airbyte/pull/60463) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60080](https://github.com/airbytehq/airbyte/pull/60080) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59639](https://github.com/airbytehq/airbyte/pull/59639) | Update dependencies |
| 0.0.20 | 2025-04-27 | [59031](https://github.com/airbytehq/airbyte/pull/59031) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58418](https://github.com/airbytehq/airbyte/pull/58418) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57983](https://github.com/airbytehq/airbyte/pull/57983) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57422](https://github.com/airbytehq/airbyte/pull/57422) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56856](https://github.com/airbytehq/airbyte/pull/56856) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56292](https://github.com/airbytehq/airbyte/pull/56292) | Update dependencies |
| 0.0.14 | 2025-03-09 | [55647](https://github.com/airbytehq/airbyte/pull/55647) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54496](https://github.com/airbytehq/airbyte/pull/54496) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54043](https://github.com/airbytehq/airbyte/pull/54043) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53575](https://github.com/airbytehq/airbyte/pull/53575) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52439](https://github.com/airbytehq/airbyte/pull/52439) | Update dependencies |
| 0.0.9 | 2025-01-18 | [52010](https://github.com/airbytehq/airbyte/pull/52010) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51444](https://github.com/airbytehq/airbyte/pull/51444) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50808](https://github.com/airbytehq/airbyte/pull/50808) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50328](https://github.com/airbytehq/airbyte/pull/50328) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49744](https://github.com/airbytehq/airbyte/pull/49744) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49395](https://github.com/airbytehq/airbyte/pull/49395) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49112](https://github.com/airbytehq/airbyte/pull/49112) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-11-04 | [48167](https://github.com/airbytehq/airbyte/pull/48167) | Update dependencies |
| 0.0.1 | 2024-10-20 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
