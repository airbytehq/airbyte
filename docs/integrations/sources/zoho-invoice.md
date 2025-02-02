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
| 0.0.8 | 2025-02-01 | [53125](https://github.com/airbytehq/airbyte/pull/53125) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52549](https://github.com/airbytehq/airbyte/pull/52549) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51937](https://github.com/airbytehq/airbyte/pull/51937) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51469](https://github.com/airbytehq/airbyte/pull/51469) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50828](https://github.com/airbytehq/airbyte/pull/50828) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50393](https://github.com/airbytehq/airbyte/pull/50393) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49444](https://github.com/airbytehq/airbyte/pull/49444) | Update dependencies |
| 0.0.1 | 2024-11-05 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
