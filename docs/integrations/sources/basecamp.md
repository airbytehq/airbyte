# Basecamp

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `account_id` | `number` | Your Basecamp Account ID.  |  |
| `start_date` | `string` | Start date — used in incremental syncs. No records before that start date will be synced.  |  |
| `client_id` | `string` | OAuth app Client ID. Go to [37Signals Launchpad](https://launchpad.37signals.com/integrations) to make a new OAuth app.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token_2` | `string` | Refresh token.  |  |

To obtain a refresh token, you'd need to register an [oauth application](https://launchpad.37signals.com/integrations) and then go through the OAuth flow. [`Basecampy`](https://github.com/phistrom/basecampy3) provides a CLI tool to do just that.

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| `projects` | `id` | DefaultPaginator | ✅ |  ❌  |
| `schedules` | `id` | DefaultPaginator | ✅ |  ❌  |
| `schedule_entries` | `id` | DefaultPaginator | ✅ |  ❌  |
| `todos` | `id` | DefaultPaginator | ✅ |  ✅  |
| `messages` | `id` | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.5 | 2025-03-08 | [54863](https://github.com/airbytehq/airbyte/pull/54863) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54222](https://github.com/airbytehq/airbyte/pull/54222) | Update dependencies |
| 0.0.3 | 2025-02-15 | [47905](https://github.com/airbytehq/airbyte/pull/47905) | Update dependencies |
| 0.0.2 | 2024-10-09 | [46660](https://github.com/airbytehq/airbyte/pull/46660) | Update dependencies |
| 0.0.1 | 2024-08-12 | | Initial release by natikgadzhi via Connector Builder |

</details>
