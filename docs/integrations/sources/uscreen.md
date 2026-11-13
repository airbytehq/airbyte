# Uscreen
Extracts customers, subscriptions, access records, groups, invoices, offers, content and user/content view analytics from the Uscreen Publisher API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Uscreen Publisher API authorization key. |  |
| `end_date` | `string` | To Date. Optional shared upper bound in RFC 3339 format. It is sent only to endpoints that support a `to` query parameter. When blank, `to` is omitted entirely. Uscreen analytics then uses its documented default of the current time. |  |
| `start_date` | `string` | From Date. Optional shared lower bound in RFC 3339 format. It is sent only to endpoints that support a `from` query parameter. When blank, `from` is omitted entirely. Uscreen analytics then uses its documented default of 12 months ago. |  |
| `general_rate_limit_calls` | `integer` | General Rate Limit Calls per Minute. Maximum number of Publisher API calls in each rolling one-minute window. Keep this at or below the quota assigned by Uscreen. | 100 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ❌  |
| customer_accesses | customer_id.id | DefaultPaginator | ✅ |  ❌  |
| customer_subscriptions | customer_id.id | No pagination | ✅ |  ❌  |
| email_topics | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| group_members | group_id.id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| offers | id | DefaultPaginator | ✅ |  ❌  |
| contents | id | DefaultPaginator | ✅ |  ❌  |
| content_playlist_items | content_id.id | No pagination | ✅ |  ❌  |
| user_views | user_id.video_id.view_start.view_end | DefaultPaginator | ✅ |  ❌  |
| content_views | user_id.content_id.video_id.view_start.view_end | DefaultPaginator | ✅ |  ❌  |
| views_summary | user_id.video_id | DefaultPaginator | ✅ |  ❌  |
| user_total_watch_time | user_id | No pagination | ✅ |  ❌  |
| content_total_watch_time | content_id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-09-03 | | Initial release by [@nktnet1](https://github.com/nktnet1) via Connector Builder |

</details>
