# Pennylane

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_time` | `string` | Start time.  |  |
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| supplier_invoices | id | DefaultPaginator | ✅ |  ✅  |

| suppliers | source_id | DefaultPaginator | ✅ |  ✅  |

| plan_items | number | DefaultPaginator | ✅ |  ❌  |

| customers | source_id | DefaultPaginator | ✅ |  ✅  |

| customer_invoices | id | DefaultPaginator | ✅ |  ✅  |

| products | source_id | DefaultPaginator | ✅ |  ✅  |

| category_groups | id | DefaultPaginator | ✅ |  ✅  |

| categories | source_id | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-21 | Initial release by natikgadzhi via Connector Builder|

</details>