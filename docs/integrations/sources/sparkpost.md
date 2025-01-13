# SparkPost
The SparkPost connector for Airbyte enables seamless integration with SparkPost’s email delivery service, allowing users to automatically sync email performance data, including delivery, open, and click metrics, into their data warehouses.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date.  |  |
| `api_prefix` | `string` | API Endpoint Prefix (`api` or `api.eu`)  | api |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| message_events | event_id | DefaultPaginator | ✅ |  ❌  |
| sending_domains | domain | No pagination | ✅ |  ❌  |
| ab_test | id | No pagination | ✅ |  ❌  |
| templates | id | No pagination | ✅ |  ❌  |
| recipients | id | No pagination | ✅ |  ❌  |
| subaccounts | id | DefaultPaginator | ✅ |  ❌  |
| snippets | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-01-11 | [51435](https://github.com/airbytehq/airbyte/pull/51435) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50792](https://github.com/airbytehq/airbyte/pull/50792) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50312](https://github.com/airbytehq/airbyte/pull/50312) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49741](https://github.com/airbytehq/airbyte/pull/49741) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49398](https://github.com/airbytehq/airbyte/pull/49398) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48315](https://github.com/airbytehq/airbyte/pull/48315) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47815](https://github.com/airbytehq/airbyte/pull/47815) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47612](https://github.com/airbytehq/airbyte/pull/47612) | Update dependencies |
| 0.0.1 | 2024-10-22 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
