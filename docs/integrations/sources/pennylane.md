# Pennylane

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_time` | `string` | Start time, used for incremental syncs. No records created before that date will be synced.  |  |
| `api_key` | `string` | Pennylane API key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| `supplier_invoices` | `id` | DefaultPaginator | ✅ |  ✅  |
| `suppliers` | `source_id` | DefaultPaginator | ✅ |  ✅  |
| `plan_items` | `number` | DefaultPaginator | ✅ |  ❌  |
| `customers` | `source_id` | DefaultPaginator | ✅ |  ✅  |
| `customer_invoices` | `id` | DefaultPaginator | ✅ |  ✅  |
| `products` | `source_id` | DefaultPaginator | ✅ |  ✅  |
| `category_groups` | `id` | DefaultPaginator | ✅ |  ✅  |
| `categories` | `source_id` | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.3 | 2024-11-04 | [47902](https://github.com/airbytehq/airbyte/pull/47902) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47536](https://github.com/airbytehq/airbyte/pull/47536) | Update dependencies |
| 0.0.1 | 2024-08-21 | | Initial release by natikgadzhi via Connector Builder |

</details>
