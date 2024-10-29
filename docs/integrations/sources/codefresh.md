# Codefresh
This connector integrates [Codefresh](https://codefresh.io) with Airbyte, enabling seamless data synchronization for analytics and pipeline monitoring. 
It provides streams like agents, builds, audit, analytics etc.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `account_id` | `string` | Account Id.  |  |
| `report_granularity` | `string` | Report Granularity.  |  |
| `report_date_range` | `array` | Report Date Range.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | _id | No pagination | ✅ |  ❌  |
| account_settings | _id | No pagination | ✅ |  ❌  |
| agents | id | No pagination | ✅ |  ❌  |
| builds | id | DefaultPaginator | ✅ |  ✅  |
| audit | id | DefaultPaginator | ✅ |  ✅  |
| analytics_metadata | reportName | No pagination | ✅ |  ❌  |
| analytics_reports |  | No pagination | ✅ |  ❌  |
| execution_contexts | _id | No pagination | ✅ |  ❌  |
| contexts | metadata | No pagination | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | metadata | DefaultPaginator | ✅ |  ❌  |
| step_types | metadata | DefaultPaginator | ✅ |  ❌  |
| helm_repos |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2024-10-28 | [47574](https://github.com/airbytehq/airbyte/pull/47574) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
