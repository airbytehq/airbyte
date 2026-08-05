# Reddit Ads
Reddit ads are paid promotional posts that appear in user feeds and within specific community threads, clearly marked as &quot;Promoted&quot;.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `start_time` | `string` | Optional UTC start date applied to all three streams, in YYYY-MM-DDTHH:MM:SSZ format. A value earlier than 24 months ago is clamped for `campaign_report`, because Reddit only serves report data for the last 24 months. | 24 months before the current date |
| `user_agent` | `string` | User Agent. A unique and descriptive user agent string in the format: platform:app_id:version (by /u/yourusername). Required for all requests. |  |
| `ad_account_id` | `string` | ad_account_id.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| ad | id | DefaultPaginator | ✅ |  ✅  |
| campaign | id | DefaultPaginator | ✅ |  ✅  |
| campaign_report | campaign_id.date | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2026-08-04 | [83603](https://github.com/airbytehq/airbyte/pull/83603) | Update dependencies |
| 0.0.3 | 2026-07-30 | [83266](https://github.com/airbytehq/airbyte/pull/83266) | Fix OAuth token refresh (stop re-refreshing the access token on every request), and recover from a stale token by refreshing it before retrying a 401; make `start_time` optional, drop its `2024-05-11T00:00:00Z` default, and apply it to all three streams with a rolling 24-month default; clamp `campaign_report` to Reddit's 24-month reporting window. Connections with `start_time` set will see the `campaign_report` window change and should reset that stream's state |
| 0.0.2 | 2026-07-28 | [83100](https://github.com/airbytehq/airbyte/pull/83100) | Update dependencies |
| 0.0.1 | 2026-07-02 | [81399](https://github.com/airbytehq/airbyte/pull/81399) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
