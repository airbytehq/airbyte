# Dust
Dust AI is an enterprise AI platform and &quot;operating system&quot; that allows teams to build custom, context-aware AI assistants without writing any code.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `end_date` | `string` | End Date. The end date for the extracted data in YYYY-MM-DD format |  |
| `start_date` | `string` | Start Date. The start date for data extraction in YYYY-MM-DD format |  |
| `bearer_token` | `string` | Bearer Token. Token needed for authentication to dust |  |
| `workspace_id` | `string` | Workspace ID. Unique string identifier for the workspace |  |

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
| 0.0.6 | 2026-08-26 | [85031](https://github.com/airbytehq/airbyte/pull/85031) | Enable acceptance tests |
| 0.0.5 | 2026-08-18 | [84577](https://github.com/airbytehq/airbyte/pull/84577) | Update dependencies |
| 0.0.4 | 2026-08-11 | [83911](https://github.com/airbytehq/airbyte/pull/83911) | Update dependencies |
| 0.0.3 | 2026-08-04 | [83458](https://github.com/airbytehq/airbyte/pull/83458) | Update dependencies |
| 0.0.2 | 2026-07-28 | [82897](https://github.com/airbytehq/airbyte/pull/82897) | Update dependencies |
| 0.0.1 | 2026-07-02 | [81402](https://github.com/airbytehq/airbyte/pull/81402) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
