# Finnworlds
Finnworlds provides data related to finance for globally traded instruments.
With this connector we can easily fetch data from various streams such as Dividends , Stock Splits , Candle Sticks etc
Docs : https://finnworlds.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `key` | `string` | API Key.  |  |
| `bond_type` | `array` | Bond Type. For example 10y, 5y, 2y... |  |
| `countries` | `array` | Countries. brazil, united states, italia, japan |  |
| `tickers` | `array` | Tickers. AAPL, T, MU, GOOG |  |
| `start_date` | `string` | Start date.  |  |
| `commodities` | `array` | Commodities. Options Available: beef, cheese, oil, ... |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| bonds | country.datetime.type | No pagination | ✅ |  ❌  |
| dividends |  | No pagination | ✅ |  ❌  |
| stock_splits | ticker.date | No pagination | ✅ |  ❌  |
| historical_candlestick | ticker.date | No pagination | ✅ |  ✅  |
| macro_calendar |  | No pagination | ✅ |  ❌  |
| macro_indicator |  | No pagination | ✅ |  ❌  |
| commodities | commodity_name.datetime | No pagination | ✅ |  ❌  |
| benchmark | datetime.country.benchmark | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-01-11 | [51099](https://github.com/airbytehq/airbyte/pull/51099) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50519](https://github.com/airbytehq/airbyte/pull/50519) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50049](https://github.com/airbytehq/airbyte/pull/50049) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49513](https://github.com/airbytehq/airbyte/pull/49513) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49206](https://github.com/airbytehq/airbyte/pull/49206) | Update dependencies |
| 0.0.1 | 2024-11-05 | | Initial release by [@marcosmarxm](https://github.com/marcosmarxm) via Connector Builder |

</details>
