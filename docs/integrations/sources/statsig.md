# Statsig
Statsig is the single platform to ship, test and analyze new features. Statsig provides the most advanced Experimentation and Feature Flagging tools available, in a platform with full-featured Product Analytics, Session Replay, and more.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `end_date` | `string` | End date.  |  |

See the [API docs](https://docs.statsig.com/http-api) for steps to generate the API key.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| audit_logs | id | DefaultPaginator | ✅ |  ❌  |
| autotunes | id | DefaultPaginator | ✅ |  ✅  |
| dynamic_configs | id | DefaultPaginator | ✅ |  ✅  |
| dynamic_configs_versions | id.version | DefaultPaginator | ✅ |  ✅  |
| dynamic_configs_rules | id | DefaultPaginator | ✅ |  ❌  |
| events |  | DefaultPaginator | ✅ |  ❌  |
| events_metrics | id | DefaultPaginator | ✅ |  ✅  |
| experiments | id | DefaultPaginator | ✅ |  ✅  |
| gates | id | DefaultPaginator | ✅ |  ✅  |
| gates_rules | id | DefaultPaginator | ✅ |  ❌  |
| holdouts | id | DefaultPaginator | ✅ |  ✅  |
| ingestion_status |  | No pagination | ✅ |  ✅  |
| ingestion_runs | runID | DefaultPaginator | ✅ |  ✅  |
| layers | id | DefaultPaginator | ✅ |  ✅  |
| metrics | id | DefaultPaginator | ✅ |  ❌  |
| metrics_values |  | DefaultPaginator | ✅ |  ❌  |
| segments | id | DefaultPaginator | ✅ |  ✅  |
| segments_ids |  | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| target_apps | id | DefaultPaginator | ✅ |  ❌  |
| users |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-27 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
