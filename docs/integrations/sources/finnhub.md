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
| 0.0.41 | 2025-12-09 | [70569](https://github.com/airbytehq/airbyte/pull/70569) | Update dependencies |
| 0.0.40 | 2025-11-25 | [69995](https://github.com/airbytehq/airbyte/pull/69995) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69464](https://github.com/airbytehq/airbyte/pull/69464) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68773](https://github.com/airbytehq/airbyte/pull/68773) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68418](https://github.com/airbytehq/airbyte/pull/68418) | Update dependencies |
| 0.0.36 | 2025-10-14 | [68033](https://github.com/airbytehq/airbyte/pull/68033) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67307](https://github.com/airbytehq/airbyte/pull/67307) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66762](https://github.com/airbytehq/airbyte/pull/66762) | Update dependencies |
| 0.0.33 | 2025-09-24 | [65752](https://github.com/airbytehq/airbyte/pull/65752) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65283](https://github.com/airbytehq/airbyte/pull/65283) | Update dependencies |
| 0.0.31 | 2025-08-16 | [64797](https://github.com/airbytehq/airbyte/pull/64797) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64398](https://github.com/airbytehq/airbyte/pull/64398) | Update dependencies |
| 0.0.29 | 2025-07-26 | [64045](https://github.com/airbytehq/airbyte/pull/64045) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63554](https://github.com/airbytehq/airbyte/pull/63554) | Update dependencies |
| 0.0.27 | 2025-07-12 | [62994](https://github.com/airbytehq/airbyte/pull/62994) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62794](https://github.com/airbytehq/airbyte/pull/62794) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62424](https://github.com/airbytehq/airbyte/pull/62424) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61947](https://github.com/airbytehq/airbyte/pull/61947) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61163](https://github.com/airbytehq/airbyte/pull/61163) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60413](https://github.com/airbytehq/airbyte/pull/60413) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59372](https://github.com/airbytehq/airbyte/pull/59372) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58879](https://github.com/airbytehq/airbyte/pull/58879) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58311](https://github.com/airbytehq/airbyte/pull/58311) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57798](https://github.com/airbytehq/airbyte/pull/57798) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57261](https://github.com/airbytehq/airbyte/pull/57261) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56497](https://github.com/airbytehq/airbyte/pull/56497) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55975](https://github.com/airbytehq/airbyte/pull/55975) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55285](https://github.com/airbytehq/airbyte/pull/55285) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54936](https://github.com/airbytehq/airbyte/pull/54936) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54381](https://github.com/airbytehq/airbyte/pull/54381) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53778](https://github.com/airbytehq/airbyte/pull/53778) | Update dependencies |
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
