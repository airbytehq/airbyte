# Holded
Holded is an ERP and business management platform covering invoicing, accounting, CRM, inventory, projects, and team management. This connector syncs contacts, products, sales documents (invoices, orders, estimates, credit notes), purchases, and projects from the Holded API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Holded API key. Generate one at https://app.holded.com/api  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| purchases | id | DefaultPaginator | ✅ |  ❌  |
| salesorders | id | DefaultPaginator | ✅ |  ❌  |
| estimates | id | DefaultPaginator | ✅ |  ❌  |
| creditnotes | id | DefaultPaginator | ✅ |  ❌  |
| purchaseorders | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-04-24 | | Initial release by [@carlosbuenosvinos](https://github.com/carlosbuenosvinos) via Connector Builder |

</details>
