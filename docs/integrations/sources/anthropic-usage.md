# Anthropic Usage
Usage &amp; Cost API endpoint integration

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date. Value cannot be older than 365 days |  |
| `admin_api_key` | `string` | Admin API key. PLACEHOLDER |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| user_activity | date.user_id | DefaultPaginator | ✅ |  ✅  |
| user_cost_report | starting_at.product.model.context_window.speed.user_id.cost_type.token_type | DefaultPaginator | ✅ |  ✅  |
| user_usage_report | starting_at.product.model.context_window.speed.user_id | DefaultPaginator | ✅ |  ✅  |
| activity_summaries | starting_at | DefaultPaginator | ✅ |  ✅  |
| project_activity | date.project_id | DefaultPaginator | ✅ |  ✅  |
| skill_activity | date.skill_name | DefaultPaginator | ✅ |  ✅  |
| connector_activity | date.connector_name | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-06-10 | | Initial release by [@mummyhen](https://github.com/mummyhen) via Connector Builder |

</details>
