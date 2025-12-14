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
| 0.0.28 | 2025-12-09 | [70811](https://github.com/airbytehq/airbyte/pull/70811) | Update dependencies |
| 0.0.27 | 2025-11-25 | [69901](https://github.com/airbytehq/airbyte/pull/69901) | Update dependencies |
| 0.0.26 | 2025-11-18 | [69521](https://github.com/airbytehq/airbyte/pull/69521) | Update dependencies |
| 0.0.25 | 2025-10-29 | [68904](https://github.com/airbytehq/airbyte/pull/68904) | Update dependencies |
| 0.0.24 | 2025-10-21 | [68382](https://github.com/airbytehq/airbyte/pull/68382) | Update dependencies |
| 0.0.23 | 2025-10-14 | [67965](https://github.com/airbytehq/airbyte/pull/67965) | Update dependencies |
| 0.0.22 | 2025-10-07 | [67162](https://github.com/airbytehq/airbyte/pull/67162) | Update dependencies |
| 0.0.21 | 2025-09-30 | [66275](https://github.com/airbytehq/airbyte/pull/66275) | Update dependencies |
| 0.0.20 | 2025-09-09 | [65643](https://github.com/airbytehq/airbyte/pull/65643) | Update dependencies |
| 0.0.19 | 2025-08-02 | [64408](https://github.com/airbytehq/airbyte/pull/64408) | Update dependencies |
| 0.0.18 | 2025-07-26 | [63806](https://github.com/airbytehq/airbyte/pull/63806) | Update dependencies |
| 0.0.17 | 2025-07-12 | [63042](https://github.com/airbytehq/airbyte/pull/63042) | Update dependencies |
| 0.0.16 | 2025-06-28 | [62136](https://github.com/airbytehq/airbyte/pull/62136) | Update dependencies |
| 0.0.15 | 2025-06-15 | [61088](https://github.com/airbytehq/airbyte/pull/61088) | Update dependencies |
| 0.0.14 | 2025-05-24 | [60678](https://github.com/airbytehq/airbyte/pull/60678) | Update dependencies |
| 0.0.13 | 2025-05-10 | [59871](https://github.com/airbytehq/airbyte/pull/59871) | Update dependencies |
| 0.0.12 | 2025-05-03 | [59362](https://github.com/airbytehq/airbyte/pull/59362) | Update dependencies |
| 0.0.11 | 2025-04-26 | [58726](https://github.com/airbytehq/airbyte/pull/58726) | Update dependencies |
| 0.0.10 | 2025-04-19 | [58254](https://github.com/airbytehq/airbyte/pull/58254) | Update dependencies |
| 0.0.9 | 2025-04-12 | [57606](https://github.com/airbytehq/airbyte/pull/57606) | Update dependencies |
| 0.0.8 | 2025-04-05 | [57157](https://github.com/airbytehq/airbyte/pull/57157) | Update dependencies |
| 0.0.7 | 2025-03-29 | [56608](https://github.com/airbytehq/airbyte/pull/56608) | Update dependencies |
| 0.0.6 | 2025-03-22 | [56114](https://github.com/airbytehq/airbyte/pull/56114) | Update dependencies |
| 0.0.5 | 2025-03-08 | [54863](https://github.com/airbytehq/airbyte/pull/54863) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54222](https://github.com/airbytehq/airbyte/pull/54222) | Update dependencies |
| 0.0.3 | 2025-02-15 | [47905](https://github.com/airbytehq/airbyte/pull/47905) | Update dependencies |
| 0.0.2 | 2024-10-09 | [46660](https://github.com/airbytehq/airbyte/pull/46660) | Update dependencies |
| 0.0.1 | 2024-08-12 | | Initial release by natikgadzhi via Connector Builder |

</details>
