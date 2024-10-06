# Codefresh
This connector integrates Codefresh with Airbyte, enabling seamless data synchronization for CI/CD analytics and pipeline monitoring. It provides streams like agents, builds, audit, analytics etc.

## Authentication
First, create an account on [codefresh](https://codefresh.io/) if you don't  already have one. Then follow [this](https://g.codefresh.io/api/#section/Authentication/API-key) step to get the API key.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `type` | `string` | Type.  |  |
| `api_key` | `string` | API Key.  |  |
| `account_id` | `string` | Account Id.  |  |
| `account_name` | `string` | Account Name.  |  |
| `report_name` | `string` | Report Name.  |  |
| `granularity` | `string` | Granularity.  |  |
| `date_range` | `array` | Date Range.  |  |
| `id` | `string` | Id.  |  |
| `entity_type` | `string` | Entity Type.  |  |
| `entity_id` | `string` | Entity Id.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts |  | No pagination | ✅ |  ❌  |
| account_settings |  | No pagination | ✅ |  ❌  |
| agents | id | No pagination | ✅ |  ❌  |
| builds |  | DefaultPaginator | ✅ |  ❌  |
| audit |  | DefaultPaginator | ✅ |  ❌  |
| analytics_metadata |  | DefaultPaginator | ✅ |  ❌  |
| analytics_reports |  | DefaultPaginator | ✅ |  ❌  |
| execution_contexts | docs | DefaultPaginator | ✅ |  ❌  |
| contexts |  | DefaultPaginator | ✅ |  ❌  |
| views |  | DefaultPaginator | ✅ |  ❌  |
| projects |  | DefaultPaginator | ✅ |  ❌  |
| pipelines | metadata | DefaultPaginator | ✅ |  ❌  |
| step_types |  | DefaultPaginator | ✅ |  ❌  |
| environments |  | DefaultPaginator | ✅ |  ❌  |
| helm_repos |  | No pagination | ✅ |  ❌  |
| favorites |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-06 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
