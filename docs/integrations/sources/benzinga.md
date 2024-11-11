# Benzinga
Benzinga is a full-service news and media company offering investors unmatched market intelligence. With expertise in breaking news and accurate financial data, Benzinga covers all aspects of financial markets spanning from corporate actions to economics to politics.
[API Docs](https://docs.benzinga.com/home)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `ticker_symbol` | `array` | Symbols.  |  |
| `interval` | `string` | Interval.  |  |
| `start_date_2` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| bull_bear_comment |  | No pagination | ✅ |  ❌  |
| analyst_insights |  | No pagination | ✅ |  ❌  |
| historical_data |  | No pagination | ✅ |  ✅  |
| delayed_quotes |  | No pagination | ✅ |  ❌  |
| market_news |  | No pagination | ✅ |  ❌  |
| option_activity |  | DefaultPaginator | ✅ |  ❌  |
| signals |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-11 | | Initial release by [@marcosmarxm](https://github.com/marcosmarxm) via Connector Builder |

</details>
