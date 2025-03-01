# Wasabi
Connector for https://www.wasabi.com stats API. 
API docs: https://docs.wasabi.com/docs/wasabi-stats-api

:::info
This connector ingest stats information from Wasabi server. 
It **does not** ingest content from files stored in Wasabi.
:::

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key format is `AccessKey:SecretKey` |  |
| `start_date` | `string` | Start date.  |  |

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
| 0.0.1 | 2024-10-25 | Initial release by [@dainiussa](https://github.com/dainiussa) via Connector Builder|

</details>
