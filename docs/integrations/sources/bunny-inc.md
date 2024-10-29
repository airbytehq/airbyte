# Bunny, Inc.
Synchronizes Bunny data

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | API Key.  |  |
| `subdomain` | `string` | Subdomain. The subdomain specific to your Bunny account or service. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| account_balances | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| entities | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| invoice_items | id | DefaultPaginator | ✅ |  ❌  |
| payments | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| plans | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| quote_charges | id | DefaultPaginator | ✅ |  ❌  |
| subscriptions | id | DefaultPaginator | ✅ |  ❌  |
| subscription_charges | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ❌  |
| tenants | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@tbpeders](https://github.com/tbpeders) via Connector Builder |

</details>
