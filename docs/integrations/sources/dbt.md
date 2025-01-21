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
| 0.0.1 | 2024-08-22 | | Initial release by natikgadzhi via Connector Builder |

</details>
