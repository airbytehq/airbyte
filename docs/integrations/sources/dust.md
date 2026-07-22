# Dust
Dust AI is an enterprise AI platform and &quot;operating system&quot; that allows teams to build custom, context-aware AI assistants without writing any code.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `end_date` | `string` | End Date. The end date for the extracted data in YYY-MM-DD format |  |
| `start_date` | `string` | Start Date. The start date for data extraction in YYY-MM-DD fromat |  |
| `bearer_token` | `string` | Bearer Token. token needed for authentication to dust |  |
| `workspace_id` | `string` | workspace ID. Unique string identifier for the workspace |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| usage_metrics | date | No pagination | ✅ |  ✅  |
| active_users | date | No pagination | ✅ |  ✅  |
| source | date.source | No pagination | ✅ |  ✅  |
| tool_usage | date.toolName | No pagination | ✅ |  ✅  |
| skill_usage | date.skillName | No pagination | ✅ |  ✅  |
| agents | agentId | No pagination | ✅ |  ❌  |
| users | userId.snapshot_date | No pagination | ✅ |  ✅  |
| messages | messageId | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-07-02 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
