# Reprise
Reprise is the demo creation platform enterprise sales and marketing teams trust to build no-code, interactive product demos that win more deals.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Reprise portal API key (Settings &gt; API Management). Exchanged for a scoped warehouse JWT via POST https://app.getreprise.com/api/warehouse/token before each replay / replicate sync. |  |
| `start_time` | `string` | start_time.  | 2022-01-01 00:00:00 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| replay_session_activity | activity_id | DefaultPaginator | ✅ |  ✅  |
| replay_session_summary | session_id | DefaultPaginator | ✅ |  ✅  |
| replay_metrics | entity_type.entity_id.window_start | DefaultPaginator | ✅ |  ✅  |
| replay_change_feed | entity_type.entity_id.ingested_at | DefaultPaginator | ✅ |  ✅  |
| replicate | session_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-21 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
