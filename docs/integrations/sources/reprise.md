# Reprise
Reprise, an enterprise-grade software platform that allows sales, marketing, and pre-sales teams to build custom, interactive product tours and fully functional cloned software environments

## Prerequisites

Access to the Reprise Data API must be included in your subscription. The connector reads five Tinybird pipes provisioned by Reprise for your workspace - confirm with Reprise support that all five exist before setting up a connection:

- `replay_session_activity` (the only pipe covered by the public [HTML Environment Data API docs](https://reprise.zendesk.com/hc/en-us/articles/18940321925659))
- `replay_session_summary`
- `replay_metrics`
- `replay_change_feed`
- `replicate_session_activity`

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Reprise portal API key (Settings &gt; API Management). Exchanged for a scoped warehouse JWT via POST https://app.getreprise.com/api/warehouse/token before each sync. |  |
| `start_time` | `string` | Start Time. Optional UTC lower bound for full refresh / first backfill of activity, summary, replicate, change_feed, and metrics (YYYY-MM-DD HH:MM:SS). Clamped to 18 months ago. Incremental activity/summary/replicate runs only re-fetch the last 3 days (lookback_window); this sets the historical floor. |  |
| `include_viewer_pii` | `boolean` | Include Viewer PII. When enabled, replicate_session_activity emits the raw viewer column (visitor email, or IP when no welcome screen is used). Disabled by default; viewer_is_internal is always emitted. | false |
| `internal_email_domains` | `string` | Internal email domains. Comma-separated email domains treated as internal for replicate_session_activity viewer_is_internal (e.g. yourcompany.com). Requires viewer_pii from the API; raw viewer is redacted by default unless include_viewer_pii is enabled. If unset, viewer_is_internal is false for all rows. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| replay_session_activity | activity_id | DefaultPaginator | ✅ |  ✅  |
| replay_session_summary | session_id | DefaultPaginator | ✅ |  ✅  |
| replay_metrics | entity_type.entity_id.window_start | DefaultPaginator | ✅ |  ✅  |
| replay_change_feed | entity_id.changed_at.change_type | DefaultPaginator | ✅ |  ✅  |
| replicate_session_activity | session_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2026-09-08 | [85636](https://github.com/airbytehq/airbyte/pull/85636) | Update dependencies |
| 0.0.1 | 2026-08-18 | [84883](https://github.com/airbytehq/airbyte/pull/84883) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
