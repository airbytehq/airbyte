# Finnhub
Finnhub is a financial data platform that provides real-time stock market, forex, and cryptocurrency data, along with extensive fundamental data, economic indicators, and alternative data for global markets. With its powerful API, Finnhub delivers actionable insights, enabling developers, financial institutions, and traders to integrate market intelligence into their applications, build trading algorithms, and track investment performance. It supports a wide range of financial metrics, including earnings reports, company profiles, and news, making it a comprehensive solution for financial analysis and market research

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |
| `end_date` | `string` | end_date.  |  |
| `start_date` | `string` | start_date.  |  |
| `company_symbol` | `string` | company_symbol.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| marketnews | id | No pagination | ✅ |  ❌  |
| stocksymbols |  | No pagination | ✅ |  ❌  |
| basicfinancials | cik | No pagination | ✅ |  ❌  |
| financialsreported | cik | No pagination | ✅ |  ❌  |
| companyprofile | ticker | No pagination | ✅ |  ❌  |
| secfilings |  | No pagination | ✅ |  ❌  |
| insidertransactions |  | No pagination | ✅ |  ❌  |
| insidersentiment |  | No pagination | ✅ |  ❌  |
| companynews |  | No pagination | ✅ |  ❌  |
| stockrecommendations |  | No pagination | ✅ |  ❌  |
| earningssurprises |  | No pagination | ✅ |  ❌  |
| stockquote |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-24 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
