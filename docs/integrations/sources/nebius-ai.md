# Nebius AI
Website: https://studio.nebius.com/
API Reference: https://studio.nebius.com/docs/api-reference

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Limit for each response objects | 20 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| models | id | No pagination | ✅ |  ✅  |
| files | id | No pagination | ✅ |  ✅  |
| file_contents | uuid | No pagination | ✅ |  ❌  |
| batches | id | No pagination | ✅ |  ✅  |
| batch_results | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-03 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
