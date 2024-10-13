# Leadfeeder

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | Leadfeeder API token.  |  |
| `start_date` | `string` | Start date for incremental syncs. Records that were updated before that date will not be synced.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| `accounts` | `id` | No pagination | ✅ |  ❌  |
| `leads` | `id` | DefaultPaginator | ✅ |  ✅  |
| `visits` | `id` | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-08-21 | | Initial release by natikgadzhi via Connector Builder |

</details>
