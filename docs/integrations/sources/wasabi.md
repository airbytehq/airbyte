# Wasabi
Connector for https://www.wasabi.com API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key format is `AccessKey:SecretKey` |  |
| `start_date` | `string` | Start date.  |  |
| `bucket_name` | `string` | Bucket name.  |  |
| `bucket_number` | `string` | Bucket number.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Standalone Utilizations |  | DefaultPaginator | ✅ |  ✅  |
| Standalone Bucket Utilizations |  | DefaultPaginator | ✅ |  ✅  |
| Standalone Bucket Utilizations for Bucket Name |  | DefaultPaginator | ✅ |  ✅  |
| Standalone Bucket Utilizations for Bucket Number |  | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-10-14 | Initial release by [@dainiussa](https://github.com/dainiussa) via Connector Builder|

</details>