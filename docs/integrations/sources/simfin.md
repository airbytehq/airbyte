# SimFin
Simfin provides financial data .
With this connector we can extract data from price data , financial statements and company info streams .
Docs https://simfin.readme.io/reference/getting-started-1

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Company Info  | id | No pagination | ✅ |  ❌  |
| Financial Statements |  | No pagination | ✅ |  ❌  |
| Price Data |  | No pagination | ✅ |  ❌  |
| companies |  | No pagination | ✅ |  ❌  |
| common_shares_outstanding |  | No pagination | ✅ |  ❌  |
| weighted_shares_outstanding |  | No pagination | ✅ |  ❌  |
| filings_by_company | filingIdentifier | No pagination | ✅ |  ❌  |
| filings_list | filingIdentifier | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
