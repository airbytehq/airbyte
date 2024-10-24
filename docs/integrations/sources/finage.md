# Finage
Real-Time Market Data Solutions for Stocks, Forex, and Crypto
This connector can be used to extract data from various APIs such as symbol-list,Aggregates,Snapshot and Technical Indicators

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `type` | `string` | Type.  Indicator type. [ DEMA, EMA, SMA, WMA, RSI, TEMA, Williams, ADX ] |  |
| `api_key` | `string` | API Key.  |  |
| `market_type` | `string` | Market type. For Example us-stock, ca-stock, in-stock, ru-stock, forex, crypto, index |  |
| `limit` | `string` | Limit. Limit of the news. Default is 10 and maximum allowed limit is 30. |  |
| `from` | `string` | From. Start date |  |
| `to` | `string` | To. End date |  |
| `time` | `string` | Time. Time interval [ daily, 1min , 5min, 15min, 30min, 1hour, 4hour ] |  |
| `period` | `string` | Period. Time period. Default is 10 |  |
| `multiply` | `string` | Multiply. Time multiplier | 1 |
| `time_aggregates` | `string` | Time aggregates. Size of the time. [minute, hour, day, week, month, quarter, year] |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Symbol List |  | DefaultPaginator | ✅ |  ❌  |
| Market News |  | No pagination | ✅ |  ❌  |
| Most Active US Stocks | symbol | No pagination | ✅ |  ❌  |
| Technical Indicators |  | No pagination | ✅ |  ❌  |
| Stock Last Quote |  | No pagination | ✅ |  ❌  |
| Stock Last Trade |  | No pagination | ✅ |  ❌  |
| US Stocks Aggregates |  | No pagination | ✅ |  ❌  |
| US Stocks Previous Close |  | No pagination | ✅ |  ❌  |
| US Stocks Snapshot | s | No pagination | ✅ |  ❌  |
| Forex Last Quote |  | No pagination | ✅ |  ❌  |
| Forex Last Trade |  | No pagination | ✅ |  ❌  |
| Forex Aggregates |  | No pagination | ✅ |  ❌  |
| Forex Previous Close |  | No pagination | ✅ |  ❌  |
| Crypto Last Quote |  | No pagination | ✅ |  ❌  |
| Crypto Aggregates |  | No pagination | ✅ |  ❌  |
|  Crypto Last Trade |  | No pagination | ✅ |  ❌  |
| Crypto Snapshot | s | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-21 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
