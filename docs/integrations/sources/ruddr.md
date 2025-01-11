# Ruddr
Ruddr connector enables seamless data synchronization from Ruddr to various data warehouses, lakes, and destinations. It simplifies data pipelines by extracting projects and analytics data, ensuring reliable and efficient data integration for real-time insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Generate it in the API Keys section of your Ruddr workspace settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| clients | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| project_members | id | DefaultPaginator | ✅ |  ❌  |
| project_tasks | id | DefaultPaginator | ✅ |  ❌  |
| expense_reports | id | DefaultPaginator | ✅ |  ❌  |
| expense_items | id | DefaultPaginator | ✅ |  ❌  |
| expense_categories | id | DefaultPaginator | ✅ |  ❌  |
| project_expense | id | DefaultPaginator | ✅ |  ❌  |
| project_budget_expenses | id | DefaultPaginator | ✅ |  ❌  |
| workspace members |  | DefaultPaginator | ✅ |  ❌  |
| opportunity_stages | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| holidays | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2025-01-11 | [51325](https://github.com/airbytehq/airbyte/pull/51325) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50241](https://github.com/airbytehq/airbyte/pull/50241) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49655](https://github.com/airbytehq/airbyte/pull/49655) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49346](https://github.com/airbytehq/airbyte/pull/49346) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49080](https://github.com/airbytehq/airbyte/pull/49080) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
