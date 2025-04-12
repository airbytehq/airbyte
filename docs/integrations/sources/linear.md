# Linear

An Airbyte connector for Linear.app.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| teams | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| cycles | id | DefaultPaginator | ✅ |  ❌  |
| issues | id | DefaultPaginator | ✅ |  ❌  |
| comments | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| attachments | id | DefaultPaginator | ✅ |  ❌  |
| issue_labels | id | DefaultPaginator | ✅ |  ❌  |
| customer_needs | id | DefaultPaginator | ✅ |  ❌  |
| customer_tiers | id | DefaultPaginator | ✅ |  ❌  |
| issue_relations | id | DefaultPaginator | ✅ |  ❌  |
| workflow_states | id | DefaultPaginator | ✅ |  ❌  |
| project_statuses | id | DefaultPaginator | ✅ |  ❌  |
| customer_statuses | id | DefaultPaginator | ✅ |  ❌  |
| project_milestones | id | DefaultPaginator | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2025-04-11 | [#57586](https://github.com/airbytehq/airbyte/pull/57586) | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) |

</details>
