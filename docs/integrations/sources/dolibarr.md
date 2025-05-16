# Dolibarr
Connector for the Dolibarr ERP/CRM REST API focused on GET operations

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `my_dolibarr_domain_url` | `string` | my_dolibarr_domain/url. enter your &quot;domain/dolibarr_url&quot; without https:// Example: mydomain.com/dolibarr |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Products list | product_id | No pagination | ✅ |  ❌  |
| Products category id list |  | No pagination | ✅ |  ❌  |
| Product categories list | category_id | No pagination | ✅ |  ❌  |
| Customer invoices list | invoice_id | DefaultPaginator | ✅ |  ❌  |
| Customer invoices lines list |  | No pagination | ✅ |  ❌  |
| Customers list |  | No pagination | ✅ |  ❌  |
| Supplier invoices list | supp_invoice_id | DefaultPaginator | ✅ |  ❌  |
| Supplier invoices lines list |  | No pagination | ✅ |  ❌  |
| Suppliers list |  | No pagination | ✅ |  ❌  |
| Internal Users | user_id | No pagination | ✅ |  ❌  |
| Company profile data |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-05-16 | | Initial release by [@leonmm2](https://github.com/leonmm2) via Connector Builder |

</details>
