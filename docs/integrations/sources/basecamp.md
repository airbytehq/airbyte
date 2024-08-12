# Basecamp

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `account_id` | `number` | Account ID.  |  |
| `start_date` | `string` | Start date.  |  |
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token_2` | `string` | Refresh token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | id | DefaultPaginator | ✅ |  ❌  |

| schedules | id | DefaultPaginator | ✅ |  ❌  |

| schedule_entries | id | DefaultPaginator | ✅ |  ❌  |

| todos | id | DefaultPaginator | ✅ |  ✅  |

| messages | id | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-12 | Initial release by natikgadzhi via Connector Builder|

</details>