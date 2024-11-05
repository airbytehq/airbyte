# Finage
Real-Time Market Data Solutions for Stocks, Forex, and Crypto
This connector can be used to extract data from various APIs such as symbol-list,Aggregates,Snapshot and Technical Indicators

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `type` | `string` | Indicator Type.  | SMA |
| `api_key` | `string` | API Key.  |  |
| `market_type` | `string` | Market type.  | us-stock |
| `limit` | `string` | Limit. Limit of the news. Default is 10 and maximum allowed limit is 30. |  |
| `from` | `string` | From. Start date |  |
| `to` | `string` | To. End date |  |
| `time` | `string` | Time Interval.  | daily |
| `period` | `string` | Period. Time period. Default is 10 |  |
| `multiply` | `string` | Multiply. Time multiplier | 1 |
| `time_aggregates` | `string` | Time aggregates. Size of the time | day |
| `symbols` | `string` | Symbols. List of symbols separated by commas  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Symbol List |  | DefaultPaginator | ✅ |  ❌  |
| Market News |  | No pagination | ✅ |  ❌  |
| Most Active US Stocks | symbol | No pagination | ✅ |  ❌  |
| Technical Indicators |  | No pagination | ✅ |  ❌  |
| us_stocks_previous_close |  | No pagination | ✅ |  ❌  |
| us_stocks_snapshot | s | No pagination | ✅ |  ❌  |
| forex_last_quote |  | No pagination | ✅ |  ❌  |
| forex_last_trade |  | No pagination | ✅ |  ❌  |
| forex_aggregates |  | No pagination | ✅ |  ❌  |
| forex_previous_close |  | No pagination | ✅ |  ❌  |
| crypto_aggregates |  | No pagination | ✅ |  ❌  |
|  crypto_last_trade |  | No pagination | ✅ |  ❌  |
| crypto_snapshot | s | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-05 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
