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
| ingest_source | id | DefaultPaginator | ✅ |  ✅  |
| ingest_source_endpoint | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-06 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
