# Finnhub
Finnhub is a financial data platform that provides real-time stock market, forex, and cryptocurrency data, along with extensive fundamental data, economic indicators, and alternative data for global markets. With its powerful API, Finnhub delivers actionable insights, enabling developers, financial institutions, and traders to integrate market intelligence into their applications, build trading algorithms, and track investment performance. It supports a wide range of financial metrics, including earnings reports, company profiles, and news, making it a comprehensive solution for financial analysis and market research

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |
| `symbols` | `array` | Companies.  |  |
| `market_news_category` | `string` | Market News Category. This parameter can be 1 of the following values general, forex, crypto, merger. | general |
| `exchange` | `string` | Exchange. More info: https://finnhub.io/docs/api/stock-symbols | US |
| `start_date_2` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| marketnews | id | No pagination | ✅ |  ❌  |
| stock_symbols |  | No pagination | ✅ |  ❌  |
| basic_financial_report | accessNumber | No pagination | ✅ |  ✅  |
| company_profile | ticker | No pagination | ✅ |  ❌  |
| sec_filings | accessNumber | No pagination | ✅ |  ✅  |
| insider_transactions |  | No pagination | ✅ |  ✅  |
| insider_sentiment |  | No pagination | ✅ |  ❌  |
| company_news |  | No pagination | ✅ |  ✅  |
| stock_recommendations |  | No pagination | ✅ |  ❌  |
| earnings_surprises | symbol.period | No pagination | ✅ |  ❌  |
| stock_quote |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-08 | [53318](https://github.com/airbytehq/airbyte/pull/53318) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52874](https://github.com/airbytehq/airbyte/pull/52874) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52341](https://github.com/airbytehq/airbyte/pull/52341) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51631](https://github.com/airbytehq/airbyte/pull/51631) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51121](https://github.com/airbytehq/airbyte/pull/51121) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50590](https://github.com/airbytehq/airbyte/pull/50590) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50046](https://github.com/airbytehq/airbyte/pull/50046) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49535](https://github.com/airbytehq/airbyte/pull/49535) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48957](https://github.com/airbytehq/airbyte/pull/48957) | Update dependencies |
| 0.0.1 | 2024-11-06 | | Initial release by [@marcosmarxm](https://github.com/marcosmarxm) via Connector Builder |

</details>
