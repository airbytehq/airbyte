# Zoho Invoice
Zoho invoice is an invoicing software used by businesses.
With this connector we can extract data from various streams such as items , contacts and invoices streams.
Docs : https://www.zoho.com/invoice/api/v3/introduction/#overview

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `organization_id` | `string` | Organization ID. TO be provided if a user belongs to multiple organizations |  |
| `region` | `string` | Region.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| items | item_id | DefaultPaginator | ✅ |  ❌  |
| users |  | DefaultPaginator | ✅ |  ❌  |
| contacts | contact_id | DefaultPaginator | ✅ |  ❌  |
| invoices | invoice_id | DefaultPaginator | ✅ |  ❌  |
| recurring_invoices | recurring_invoice_id | DefaultPaginator | ✅ |  ❌  |
| customer_payments | payment_id | DefaultPaginator | ✅ |  ❌  |
| credit notes | creditnote_id | DefaultPaginator | ✅ |  ❌  |
| expenses | expense_id | DefaultPaginator | ✅ |  ❌  |
| taxes | tax_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.21 | 2025-06-15 | [61245](https://github.com/airbytehq/airbyte/pull/61245) | Update dependencies |
| 0.0.20 | 2025-05-24 | [60742](https://github.com/airbytehq/airbyte/pull/60742) | Update dependencies |
| 0.0.19 | 2025-05-10 | [59542](https://github.com/airbytehq/airbyte/pull/59542) | Update dependencies |
| 0.0.18 | 2025-04-26 | [58937](https://github.com/airbytehq/airbyte/pull/58937) | Update dependencies |
| 0.0.17 | 2025-04-19 | [58548](https://github.com/airbytehq/airbyte/pull/58548) | Update dependencies |
| 0.0.16 | 2025-04-12 | [58025](https://github.com/airbytehq/airbyte/pull/58025) | Update dependencies |
| 0.0.15 | 2025-04-05 | [57401](https://github.com/airbytehq/airbyte/pull/57401) | Update dependencies |
| 0.0.14 | 2025-03-29 | [56815](https://github.com/airbytehq/airbyte/pull/56815) | Update dependencies |
| 0.0.13 | 2025-03-22 | [56332](https://github.com/airbytehq/airbyte/pull/56332) | Update dependencies |
| 0.0.12 | 2025-03-09 | [55667](https://github.com/airbytehq/airbyte/pull/55667) | Update dependencies |
| 0.0.11 | 2025-03-01 | [54640](https://github.com/airbytehq/airbyte/pull/54640) | Update dependencies |
| 0.0.10 | 2025-02-15 | [54117](https://github.com/airbytehq/airbyte/pull/54117) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53591](https://github.com/airbytehq/airbyte/pull/53591) | Update dependencies |
| 0.0.8 | 2025-02-01 | [53125](https://github.com/airbytehq/airbyte/pull/53125) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52549](https://github.com/airbytehq/airbyte/pull/52549) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51937](https://github.com/airbytehq/airbyte/pull/51937) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51469](https://github.com/airbytehq/airbyte/pull/51469) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50828](https://github.com/airbytehq/airbyte/pull/50828) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50393](https://github.com/airbytehq/airbyte/pull/50393) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49444](https://github.com/airbytehq/airbyte/pull/49444) | Update dependencies |
| 0.0.1 | 2024-11-05 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
