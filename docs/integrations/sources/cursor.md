# Cursor
Sync Cursor Teams usage, per-seat spend, and per-event cost data from the Cursor Admin API into your warehouse. Captures Cursor&#39;s rolling usage and spend window into permanent storage, so history accrues from the day you install.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Cursor Admin API key (starts with crsr_). Create one in the Cursor dashboard under Settings &gt; Admin &gt; API Keys. |  |
| `start_date` | `string` | Start Date. UTC date to start syncing daily_usage and usage_events from, in YYYY-MM-DD format. Cursor only retains a rolling window of usage data, so dates older than that window return nothing. History accrues forward from the day you install this connector. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| members | email | No pagination | ✅ |  ❌  |
| daily_usage | date.email | No pagination | ✅ |  ✅  |
| spend | email | DefaultPaginator | ✅ |  ❌  |
| usage_events | timestamp.userEmail.model | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-23 | | Initial release by [@dhlotter](https://github.com/dhlotter) via Connector Builder |

</details>
