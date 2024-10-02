# Google Calendar
Solves https://github.com/airbytehq/airbyte/issues/45995

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token_2` | `string` | Refresh token.  |  |
| `calendarid` | `string` | Calendar Id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| colors |  | No pagination | ✅ |  ❌  |
| settings | id | DefaultPaginator | ✅ |  ❌  |
| calendarlist | id | DefaultPaginator | ✅ |  ❌  |
| calendars | id | DefaultPaginator | ✅ |  ❌  |
| events |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-02 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
