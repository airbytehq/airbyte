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
| 0.0.4 | 2025-04-19 | [58523](https://github.com/airbytehq/airbyte/pull/58523) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57856](https://github.com/airbytehq/airbyte/pull/57856) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57348](https://github.com/airbytehq/airbyte/pull/57348) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56989](https://github.com/airbytehq/airbyte/pull/56989) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
