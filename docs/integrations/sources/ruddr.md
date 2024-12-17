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
| 0.0.1 | 2024-11-08 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
