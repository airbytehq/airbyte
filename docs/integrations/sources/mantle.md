# Mantle
This connector use the Mantle API to get customers and subscriptions streams

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ✅  |
| subscriptions | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-09-04 | [65150](https://github.com/airbytehq/airbyte/pull/65150) | Fix pagination for Subscriptions |
| 0.0.2 | 2025-08-23 | [65182](https://github.com/airbytehq/airbyte/pull/65182) | Update dependencies |
| 0.0.1 | 2025-08-13 | | Initial release by [@KimPlv](https://github.com/KimPlv) via Connector Builder |

</details>
