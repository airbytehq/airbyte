# Polygon Financial Connector
A homebrewed connector to pull financial data from Polygon.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `olhc_stock_tickers` | `array` | Stock Tickers. The list of stocks to request data for. Used in all endpoints in this connector: - Stock OLHC Aggregates - Stock News - Stock Financials - Ticker Details - Related Companies |  |
| `stock_window_multiplier` | `integer` | Stock Window Multiplier. Used in &quot;Stock OLHC Aggregated endpoint&quot;. The window multiplier to use for a time window. If timespan = ‘minute’ and multiplier = ‘5’ then 5-minute bars will be returned. |  |
| `stock_window_timespan` | `string` | Stock Window Timespan. Used in &quot;Stock OLHC Aggregates&quot; endpoint. The size of the time window that is used in conjuntion with the multiplier to get the aggregates for Open-Close-High-Low  stock data. |  |
| `from_date` | `string` | From Date. Lower end of the datetime range. Used in all endpoints, except: - Related Copmpanies |  |
| `to_date` | `string` | To Date. Upper end of the datetime range. Used in all endpoints, except: - Related Copmpanies |  |
| `news_per_page_limit` | `number` | News Per Page Limit. The amount of news to recover en every paginated request. Used in all endpoints that support pagination: - Stock OLHC Aggregates - Stock News - Stock Financials |  |
| `financials_timeframe` | `string` | Financials Timeframe. Used only in &quot;stock Financials&quot; endpoint. The type of financial report: Quarterly or Anually. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Stock OLHC Aggregates | ticker.t | DefaultPaginator | ✅ |  ❌  |
| Stock News |  | DefaultPaginator | ✅ |  ✅  |
| Stock Financials | cik.filing_date | DefaultPaginator | ✅ |  ✅  |
| Ticker Details | ticker | No pagination | ✅ |  ❌  |
| Related Companies | source_ticker.process_date.ticker | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-10-16 | Initial release by [@hector6298](https://github.com/hector6298) via Connector Builder|

</details>