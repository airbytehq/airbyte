# Svix
Website: https://dashboard.svix.com/
API Reference: https://api.svix.com/docs#section/Introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| applications | id | DefaultPaginator | ✅ |  ✅  |
| event_types | uuid | DefaultPaginator | ✅ |  ✅  |
| tokens | id | DefaultPaginator | ✅ |  ✅  |
| endpoints | id | DefaultPaginator | ✅ |  ✅  |
| integrations | id | DefaultPaginator | ✅ |  ✅  |
| ingest_source | id | DefaultPaginator | ✅ |  ✅  |
| ingest_source_endpoint | id | DefaultPaginator | ✅ |  ✅  |
| webhook_endpoint | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58429](https://github.com/airbytehq/airbyte/pull/58429) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57997](https://github.com/airbytehq/airbyte/pull/57997) | Update dependencies |
| 0.0.1 | 2025-04-06 | [57495](https://github.com/airbytehq/airbyte/pull/57495) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
