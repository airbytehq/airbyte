# Airbyte


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | client_id.  |  |
| `start_date` | `string` | Start date.  |  |
| `client_secret` | `string` | client_secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Jobs | jobId | DefaultPaginator | ✅ |  ✅  |
| Connections | connectionId | DefaultPaginator | ✅ |  ❌  |
| Workspaces | workspaceId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-27 | Initial release by [@johnwasserman](https://github.com/johnwasserman) via Connector Builder|

</details>