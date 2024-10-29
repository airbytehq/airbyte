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
| 0.0.1 | 2024-10-20 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
