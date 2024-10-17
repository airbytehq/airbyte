# SparkPost
The SparkPost connector for Airbyte enables seamless integration with SparkPost’s email delivery service, allowing users to automatically sync email performance data, including delivery, open, and click metrics, into their data warehouses.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `events` | `string` | Events.  |  |
| `recipients` | `string` | Recipients.  |  |
| `templates` | `string` | Templates.  |  |
| `from` | `string` | From.  |  |
| `metrics` | `array` | Metrics.  |  |
| `region` | `string` | Region.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| message_events | event_id | DefaultPaginator | ✅ |  ❌  |
| sending_domains | domain | No pagination | ✅ |  ❌  |
| ab_test | id | No pagination | ✅ |  ❌  |
| templates | id | No pagination | ✅ |  ❌  |
| recipients | id | No pagination | ✅ |  ❌  |
| metrics_summary |  | No pagination | ✅ |  ❌  |
| subaccounts | id | DefaultPaginator | ✅ |  ❌  |
| engagement_details |  | DefaultPaginator | ✅ |  ❌  |
| rejection_reason_metrics |  | DefaultPaginator | ✅ |  ❌  |
| metrics |  | No pagination | ✅ |  ❌  |
| metrics_by_template | template_id | DefaultPaginator | ✅ |  ❌  |
| snippets | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-17 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
