# Codefresh
This connector integrates Codefresh with Airbyte, enabling seamless data synchronization for analytics and pipeline monitoring. It provides streams like agents, builds, audit, analytics etc.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `type` | `string` | Type.  |  |
| `api_key` | `string` | API Key.  |  |
| `account_id` | `string` | Account Id.  |  |
| `account_name` | `string` | Account Name.  |  |
| `report_name` | `string` | Report Name.  |  |
| `report_granularity` | `string` | Report Granularity.  |  |
| `report_date_range` | `array` | Report Date Range.  |  |
| `entity_type` | `string` | Entity Type.  |  |
| `entity_id` | `string` | Entity Id.  |  |
| `start_date` | `string` | Start date.  |  |
| `from` | `string` | From.  |  |
| `to` | `string` | To.  |  |
| `startdate` | `string` | startDate.  |  |
| `enddate` | `string` | endDate.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | _id | No pagination | ✅ |  ❌  |
| account_settings | _id | No pagination | ✅ |  ❌  |
| agents | id | No pagination | ✅ |  ❌  |
| builds | id | DefaultPaginator | ✅ |  ✅  |
| audit | id | DefaultPaginator | ✅ |  ✅  |
| analytics_metadata | reportName | No pagination | ✅ |  ❌  |
| analytics_reports |  | DefaultPaginator | ✅ |  ❌  |
| execution_contexts | _id | DefaultPaginator | ✅ |  ❌  |
| contexts | metadata | DefaultPaginator | ✅ |  ❌  |
| views |  | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | metadata | DefaultPaginator | ✅ |  ❌  |
| step_types | metadata | No pagination | ✅ |  ❌  |
| environments |  | DefaultPaginator | ✅ |  ❌  |
| helm_repos |  | No pagination | ✅ |  ❌  |
| favorites | _id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-08 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
