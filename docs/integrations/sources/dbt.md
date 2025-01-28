# DBT

DBT Source Connector provides streams with your DBT projects, repositories, users, environments, and runs from DBT Cloud.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | DBT API token.  |  |
| `account_id` | `string` | Your DBT account ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| `runs` | `id` | DefaultPaginator | ✅ |  ❌  |
| `projects` | `id` | DefaultPaginator | ✅ |  ❌  |
| `repositories` | `id` | DefaultPaginator | ✅ |  ❌  |
| `users` | `id` | DefaultPaginator | ✅ |  ❌  |
| `environments` | `id` | DefaultPaginator | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.7 | 2025-01-11 | [51086](https://github.com/airbytehq/airbyte/pull/51086) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50556](https://github.com/airbytehq/airbyte/pull/50556) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50035](https://github.com/airbytehq/airbyte/pull/50035) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49499](https://github.com/airbytehq/airbyte/pull/49499) | Update dependencies |
| 0.0.3 | 2024-12-12 | [47748](https://github.com/airbytehq/airbyte/pull/47748) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47460](https://github.com/airbytehq/airbyte/pull/47460) | Update dependencies |
| 0.0.1 | 2024-08-22 | | Initial release by natikgadzhi via Connector Builder |

</details>
