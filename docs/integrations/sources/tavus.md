# Tavus
Website: https://platform.tavus.io/
API Reference: https://docs.tavus.io/api-reference/phoenix-replica-model/get-replicas

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Tavus API key. You can find this in your Tavus account settings or API dashboard. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| replicas | replica_id | DefaultPaginator | ✅ |  ✅  |
| videos | video_id | DefaultPaginator | ✅ |  ❌  |
| conversations | conversation_id | DefaultPaginator | ✅ |  ✅  |
| personas | persona_id | DefaultPaginator | ✅ |  ✅  |
| speeches | speech_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-05 | []() | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
