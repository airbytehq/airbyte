# Tremendous
Tremendous connector  enables seamless integration with Tremendous API. This connector allows organizations to automate and sync reward, incentive, and payout data, tapping into 2000+ payout methods, including ACH, gift cards, PayPal, and prepaid cards, all from a single platform.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. You can generate an API key through the Tremendous dashboard under Team Settings &gt; Developers. Save the key once you’ve generated it. |  |
| `environment` | `string` | Environment.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orders | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| funding_sources | id | DefaultPaginator | ✅ |  ❌  |
| account_members | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| exchange_rates |  | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |
| balance_transactions |  | DefaultPaginator | ✅ |  ❌  |
| rewards | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
