# Netvisor
Access your company&#39;s Netvisor data for reporting and analysis. Supports Netvisor test and production environments.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `language` | `string` | Response language. Language for Netvisor&#39;s response messages, mainly errors. Choose FI (Finnish), SE (Swedish), or EN (English). | EN |
| `company_id` | `string` | Company business ID. Business ID of the Netvisor company to read. |  |
| `partner_id` | `string` | Partner ID. Partner ID for the same test or production environment as the customer API identifiers. |  |
| `start_date` | `string` | Sync history start date. Start date for ledger changes and daily account balances. Ledger history uses entry modification dates; balances use accounting dates and are refreshed through today (UTC) on every sync. Choose a date before the earliest history you need. Reference data is always retrieved in full. |  |
| `customer_id` | `string` | Customer API ID. Customer API identifier with read access. |  |
| `environment` | `string` | Environment. Netvisor environment to connect to. Use customer and partner credentials issued for the selected environment. |  |
| `partner_key` | `string` | Partner key.  |  |
| `window_days` | `integer` | Days per request. Number of days of ledger changes or daily account balances to retrieve per request. Smaller values reduce response sizes; larger values reduce the number of requests. | 30 |
| `customer_key` | `string` | Customer API key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account_balances | company_id.Netvisorkey.Date | NoPagination | ✅ |  ❌  |
| accounting_ledger | company_id.NetvisorKey | NoPagination | ✅ |  ✅  |
| accounting_locks | company_id | NoPagination | ✅ |  ❌  |
| accounting_periods | company_id.NetvisorKey | NoPagination | ✅ |  ❌  |
| accounts | company_id.NetvisorKey | NoPagination | ✅ |  ❌  |
| bank_accounts | company_id.IBAN | NoPagination | ✅ |  ❌  |
| default_accounts | company_id | NoPagination | ✅ |  ❌  |
| default_voucher_types | company_id | NoPagination | ✅ |  ❌  |
| dimensions | company_id.Netvisorkey | NoPagination | ✅ |  ❌  |
| voucher_types | company_id.NetvisorKey | NoPagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-10-19 | | Initial release by [@jaska120](https://github.com/jaska120) via Connector Builder |

</details>
