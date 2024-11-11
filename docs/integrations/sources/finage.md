# Finage
Real-Time Market Data Solutions for Stocks, Forex, and Crypto
This connector can be used to extract data from various APIs such as symbol-list,Aggregates,Snapshot and Technical Indicators

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `symbols` | `array` | Symbols. List of symbols  |  |
| `tech_indicator_type` | `string` | Technical Indicator Type. One of DEMA, EMA, SMA, WMA, RSI, TEMA, Williams, ADX  | SMA |
| `time` | `string` | Time Interval.  | daily |
| `period` | `string` | Period. Time period. Default is 10 |  |
| `time_aggregates` | `string` | Time aggregates. Size of the time | day |
| `time_period` | `string` | Time Period. Time Period for cash flow stmts |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| market_news |  | No pagination | ✅ |  ❌  |
| most_active_us_stocks | symbol | No pagination | ✅ |  ❌  |
| technical_indicators |  | No pagination | ✅ |  ❌  |
| economic_calendar |  | No pagination | ✅ |  ✅  |
| earning_calendar |  | No pagination | ✅ |  ❌  |
| delisted_companies | symbol | No pagination | ✅ |  ❌  |
| ipo_calendar | symbol | No pagination | ✅ |  ✅  |
| historical_stock_split  |  | No pagination | ✅ |  ❌  |
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
| 0.0.1 | 2024-11-11 | | Initial release by [@marcosmarxm](https://github.com/marcosmarxm) via Connector Builder |

</details>
