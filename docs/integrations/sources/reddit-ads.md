# Reddit Ads
Reddit ads are paid promotional posts that appear in user feeds and within specific community threads, clearly marked as &quot;Promoted&quot;.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `start_time` | `string` | start_time.  | 2024-05-11T00:00:00Z |
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
| 0.0.3 | 2026-07-30 | [83266](https://github.com/airbytehq/airbyte/pull/83266) | Fix OAuth token refresh by removing incorrect token_expiry_date_format |
| 0.0.2 | 2026-07-28 | [83100](https://github.com/airbytehq/airbyte/pull/83100) | Update dependencies |
| 0.0.1 | 2026-07-02 | [81399](https://github.com/airbytehq/airbyte/pull/81399) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
