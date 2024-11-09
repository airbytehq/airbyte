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
| `symbols` | `array` | Symbols. List of symbols  |  |
| `time_period` | `string` | Time Period. Time Period for cash flow stmts |  |
| `stmt_limit` | `string` | Statement Limit.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| market_news |  | No pagination | ✅ |  ❌  |
| most_active_us_stocks | symbol | No pagination | ✅ |  ❌  |
| technical_indicators |  | No pagination | ✅ |  ❌  |
| us_stocks_previous_close |  | No pagination | ✅ |  ❌  |
| market_status |  | No pagination | ✅ |  ❌  |
| economic_calendar |  | No pagination | ✅ |  ❌  |
| earning_calendar |  | No pagination | ✅ |  ❌  |
| delisted_companies | symbol | No pagination | ✅ |  ❌  |
| ipo_calendar | symbol | No pagination | ✅ |  ❌  |
| stocks_split |  | No pagination | ✅ |  ❌  |
| historical_stock_split  |  | No pagination | ✅ |  ❌  |
| dividends_calendar |  | No pagination | ✅ |  ❌  |
| historical_dividends_calendar |  | No pagination | ✅ |  ❌  |
| cash_flow_statements | date.symbol | No pagination | ✅ |  ❌  |
| balance_sheet_statements | date.symbol | No pagination | ✅ |  ❌  |
| income_statement | date.symbol | No pagination | ✅ |  ❌  |
| institutional_holders | holder | No pagination | ✅ |  ❌  |
| mutual_fund_holder |  | No pagination | ✅ |  ❌  |
| most_gainers | symbol | No pagination | ✅ |  ❌  |
| most_losers | symbol | No pagination | ✅ |  ❌  |
| sector_performance | sector | No pagination | ✅ |  ❌  |
| shares_float |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
