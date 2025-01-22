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
| 0.0.8 | 2025-01-18 | [51986](https://github.com/airbytehq/airbyte/pull/51986) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51440](https://github.com/airbytehq/airbyte/pull/51440) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50755](https://github.com/airbytehq/airbyte/pull/50755) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50310](https://github.com/airbytehq/airbyte/pull/50310) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49776](https://github.com/airbytehq/airbyte/pull/49776) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49419](https://github.com/airbytehq/airbyte/pull/49419) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47473](https://github.com/airbytehq/airbyte/pull/47473) | Update dependencies |
| 0.0.1 | 2024-09-27 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
