# SparkPost
The SparkPost connector for Airbyte enables seamless integration with SparkPost’s email delivery service, allowing users to automatically sync email performance data, including delivery, templates, and click metrics etc into their data warehouses.

## Authentication
Before you can use SparkPost's REST API you will need to have a valid SparkPost API key. Follow [these](https://support.sparkpost.com/docs/getting-started/create-api-keys) steps to create a SparkPost API key.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `events` | `string` | Events.  |  |
| `recipients` | `string` | Recipients.  |  |
| `templates` | `string` | Templates.  |  |
| `domain` | `string` | Domain.  |  |
| `from` | `string` | From.  |  |
| `metrics` | `array` | Metrics.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| search_message_events | event_id | No pagination | ✅ |  ❌  |
| sending_domains | domain | No pagination | ✅ |  ❌  |
| ab_test | id | No pagination | ✅ |  ❌  |
| templates | id | No pagination | ✅ |  ❌  |
| recipients | id | No pagination | ✅ |  ❌  |
| metrics_summary |  | No pagination | ✅ |  ❌  |
| subaccounts | id | DefaultPaginator | ✅ |  ❌  |
| engagement_details |  | No pagination | ✅ |  ❌  |
| rejection_reason_metrics |  | DefaultPaginator | ✅ |  ❌  |
| metrics |  | No pagination | ✅ |  ❌  |
| metrics_by_template | template_id | DefaultPaginator | ✅ |  ❌  |
| snippets | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-10 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
