# Veeqo
Veeqo Airbyte connector for Veeqo enables seamless data integration between Veeqo&#39;s inventory and order management platform and various data warehouses or applications. It allows users to sync Veeqo data such as orders, products, inventory levels, and more, making it easier to analyze and manage e-commerce operations. This connector streamlines data workflows, ensuring up-to-date and accurate information for better business insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| orders | id | DefaultPaginator | ✅ |  ✅  |
| returns | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| purchase_orders | id | DefaultPaginator | ✅ |  ❌  |
| suppliers | id | DefaultPaginator | ✅ |  ❌  |
| company |  | DefaultPaginator | ✅ |  ❌  |
| warehouses | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| stores | id | DefaultPaginator | ✅ |  ❌  |
| delivery_methods | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-01-11 | [51456](https://github.com/airbytehq/airbyte/pull/51456) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50756](https://github.com/airbytehq/airbyte/pull/50756) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50344](https://github.com/airbytehq/airbyte/pull/50344) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49789](https://github.com/airbytehq/airbyte/pull/49789) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49408](https://github.com/airbytehq/airbyte/pull/49408) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48254](https://github.com/airbytehq/airbyte/pull/48254) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47811](https://github.com/airbytehq/airbyte/pull/47811) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47488](https://github.com/airbytehq/airbyte/pull/47488) | Update dependencies |
| 0.0.1 | 2024-10-17 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
