# Claude
Designed for organizations on the Claude Platform, this API provides programmatic access to daily aggregated usage metrics.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Claude organization-level Analytics API key (read:analytics scope) |  |
| `end_date` | `string` | End Date. Optional end date override in YYYY-MM-DD format (capped at 3 days ago UTC for engagement streams; cost/usage default to today UTC) |  |
| `start_date` | `string` | Start Date. Start date for data extraction in YYYY-MM-DD format | 2026-01-01 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | user_id.date | DefaultPaginator | ✅ |  ✅  |
| chat_projects | project_id.date | DefaultPaginator | ✅ |  ✅  |
| skills | skill_name.date | DefaultPaginator | ✅ |  ✅  |
| connectors | connector_name.date | DefaultPaginator | ✅ |  ✅  |
| summaries | starting_date | No pagination | ✅ |  ✅  |
| user_usage_report | date.actor_user_id.product.model | DefaultPaginator | ✅ |  ✅  |
| user_cost_report | date.actor_user_id.product.model.cost_type | DefaultPaginator | ✅ |  ✅  |
| usage_report | starting_at | DefaultPaginator | ✅ |  ✅  |
| cost_report | starting_at | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-02 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
