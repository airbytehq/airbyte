# Salesflare
Salesflare is a CRM tool for small and medium businesses.
Using this connector we can extract data from various streams such as opportunities , workflows and pipelines.
Docs : https://api.salesflare.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Enter you api key like this : Bearer YOUR_API_KEY |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| opportunities | id | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| persons | id | No pagination | ✅ |  ❌  |
| email data sources | id | No pagination | ✅ |  ❌  |
| custom field types | id | No pagination | ✅ |  ❌  |
| pipelines | id | No pagination | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-01 | [52960](https://github.com/airbytehq/airbyte/pull/52960) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52486](https://github.com/airbytehq/airbyte/pull/52486) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51918](https://github.com/airbytehq/airbyte/pull/51918) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51311](https://github.com/airbytehq/airbyte/pull/51311) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50695](https://github.com/airbytehq/airbyte/pull/50695) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50234](https://github.com/airbytehq/airbyte/pull/50234) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49660](https://github.com/airbytehq/airbyte/pull/49660) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49325](https://github.com/airbytehq/airbyte/pull/49325) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49078](https://github.com/airbytehq/airbyte/pull/49078) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-07 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
