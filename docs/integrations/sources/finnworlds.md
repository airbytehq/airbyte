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
| 0.0.40 | 2025-12-09 | [70575](https://github.com/airbytehq/airbyte/pull/70575) | Update dependencies |
| 0.0.39 | 2025-11-25 | [69978](https://github.com/airbytehq/airbyte/pull/69978) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69451](https://github.com/airbytehq/airbyte/pull/69451) | Update dependencies |
| 0.0.37 | 2025-10-29 | [68821](https://github.com/airbytehq/airbyte/pull/68821) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68474](https://github.com/airbytehq/airbyte/pull/68474) | Update dependencies |
| 0.0.35 | 2025-10-14 | [68035](https://github.com/airbytehq/airbyte/pull/68035) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67314](https://github.com/airbytehq/airbyte/pull/67314) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66777](https://github.com/airbytehq/airbyte/pull/66777) | Update dependencies |
| 0.0.32 | 2025-09-24 | [65789](https://github.com/airbytehq/airbyte/pull/65789) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65253](https://github.com/airbytehq/airbyte/pull/65253) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64796](https://github.com/airbytehq/airbyte/pull/64796) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64360](https://github.com/airbytehq/airbyte/pull/64360) | Update dependencies |
| 0.0.28 | 2025-07-26 | [64024](https://github.com/airbytehq/airbyte/pull/64024) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63565](https://github.com/airbytehq/airbyte/pull/63565) | Update dependencies |
| 0.0.26 | 2025-07-12 | [63018](https://github.com/airbytehq/airbyte/pull/63018) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62377](https://github.com/airbytehq/airbyte/pull/62377) | Update dependencies |
| 0.0.24 | 2025-06-22 | [62006](https://github.com/airbytehq/airbyte/pull/62006) | Update dependencies |
| 0.0.23 | 2025-06-14 | [60347](https://github.com/airbytehq/airbyte/pull/60347) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60000](https://github.com/airbytehq/airbyte/pull/60000) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59379](https://github.com/airbytehq/airbyte/pull/59379) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58844](https://github.com/airbytehq/airbyte/pull/58844) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58331](https://github.com/airbytehq/airbyte/pull/58331) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57756](https://github.com/airbytehq/airbyte/pull/57756) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57245](https://github.com/airbytehq/airbyte/pull/57245) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56478](https://github.com/airbytehq/airbyte/pull/56478) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55980](https://github.com/airbytehq/airbyte/pull/55980) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55287](https://github.com/airbytehq/airbyte/pull/55287) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54923](https://github.com/airbytehq/airbyte/pull/54923) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54412](https://github.com/airbytehq/airbyte/pull/54412) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53773](https://github.com/airbytehq/airbyte/pull/53773) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53374](https://github.com/airbytehq/airbyte/pull/53374) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52806](https://github.com/airbytehq/airbyte/pull/52806) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52340](https://github.com/airbytehq/airbyte/pull/52340) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51630](https://github.com/airbytehq/airbyte/pull/51630) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51099](https://github.com/airbytehq/airbyte/pull/51099) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50519](https://github.com/airbytehq/airbyte/pull/50519) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50049](https://github.com/airbytehq/airbyte/pull/50049) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49513](https://github.com/airbytehq/airbyte/pull/49513) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49206](https://github.com/airbytehq/airbyte/pull/49206) | Update dependencies |
| 0.0.1 | 2024-11-05 | | Initial release by [@marcosmarxm](https://github.com/marcosmarxm) via Connector Builder |

</details>
