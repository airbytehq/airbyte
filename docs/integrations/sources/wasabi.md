# Wasabi
Connector for https://www.wasabi.com API. API docs: https://docs.wasabi.com/docs/wasabi-stats-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `api_key` | `string` | API Key. The API key format is `AccessKey:SecretKey` |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Standalone Utilizations |  | DefaultPaginator | ✅ |  ✅  |
| Standalone Bucket Utilizations |  | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-10-21 | Initial release by [@dainiussa](https://github.com/dainiussa) via Connector Builder|

</details>