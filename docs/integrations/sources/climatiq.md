# Climatiq
Website: https://www.climatiq.io/
API Reference: http://climatiq.io/docs/api-reference/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Climatiq API key. You can find it by logging into your Climatiq account and navigating to the API key section. Refer to https://www.climatiq.io/docs/guides/how-tos/getting-api-key for more details. |  |
| `query` | `string` | Search query for search streams. Search queries could include name for search endpoints | Carbon |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| search | id | DefaultPaginator | ✅ |  ❌  |
| unit_types | unit_type | DefaultPaginator | ✅ |  ❌  |
| data_versions | uuid | No pagination | ✅ |  ❌  |
| compute_metadata | uuid | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-05 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
