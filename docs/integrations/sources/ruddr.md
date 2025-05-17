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
| 0.0.21 | 2025-05-17 | [60454](https://github.com/airbytehq/airbyte/pull/60454) | Update dependencies |
| 0.0.20 | 2025-05-10 | [60089](https://github.com/airbytehq/airbyte/pull/60089) | Update dependencies |
| 0.0.19 | 2025-05-04 | [59575](https://github.com/airbytehq/airbyte/pull/59575) | Update dependencies |
| 0.0.18 | 2025-04-27 | [58996](https://github.com/airbytehq/airbyte/pull/58996) | Update dependencies |
| 0.0.17 | 2025-04-19 | [58403](https://github.com/airbytehq/airbyte/pull/58403) | Update dependencies |
| 0.0.16 | 2025-04-12 | [57948](https://github.com/airbytehq/airbyte/pull/57948) | Update dependencies |
| 0.0.15 | 2025-04-05 | [57488](https://github.com/airbytehq/airbyte/pull/57488) | Update dependencies |
| 0.0.14 | 2025-03-29 | [56749](https://github.com/airbytehq/airbyte/pull/56749) | Update dependencies |
| 0.0.13 | 2025-03-22 | [56206](https://github.com/airbytehq/airbyte/pull/56206) | Update dependencies |
| 0.0.12 | 2025-03-08 | [54612](https://github.com/airbytehq/airbyte/pull/54612) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53989](https://github.com/airbytehq/airbyte/pull/53989) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53478](https://github.com/airbytehq/airbyte/pull/53478) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52963](https://github.com/airbytehq/airbyte/pull/52963) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52511](https://github.com/airbytehq/airbyte/pull/52511) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51925](https://github.com/airbytehq/airbyte/pull/51925) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51325](https://github.com/airbytehq/airbyte/pull/51325) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50241](https://github.com/airbytehq/airbyte/pull/50241) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49655](https://github.com/airbytehq/airbyte/pull/49655) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49346](https://github.com/airbytehq/airbyte/pull/49346) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49080](https://github.com/airbytehq/airbyte/pull/49080) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
