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
| 0.0.12 | 2025-12-09 | [70750](https://github.com/airbytehq/airbyte/pull/70750) | Update dependencies |
| 0.0.11 | 2025-11-25 | [70132](https://github.com/airbytehq/airbyte/pull/70132) | Update dependencies |
| 0.0.10 | 2025-11-18 | [69545](https://github.com/airbytehq/airbyte/pull/69545) | Update dependencies |
| 0.0.9 | 2025-10-29 | [69069](https://github.com/airbytehq/airbyte/pull/69069) | Update dependencies |
| 0.0.8 | 2025-10-21 | [68445](https://github.com/airbytehq/airbyte/pull/68445) | Update dependencies |
| 0.0.7 | 2025-10-14 | [67809](https://github.com/airbytehq/airbyte/pull/67809) | Update dependencies |
| 0.0.6 | 2025-10-07 | [67377](https://github.com/airbytehq/airbyte/pull/67377) | Update dependencies |
| 0.0.5 | 2025-09-30 | [66339](https://github.com/airbytehq/airbyte/pull/66339) | Update dependencies |
| 0.0.4 | 2025-09-09 | [65746](https://github.com/airbytehq/airbyte/pull/65746) | Update dependencies |
| 0.0.3 | 2025-09-04 | [65150](https://github.com/airbytehq/airbyte/pull/65150) | Fix pagination for Subscriptions |
| 0.0.2 | 2025-08-23 | [65182](https://github.com/airbytehq/airbyte/pull/65182) | Update dependencies |
| 0.0.1 | 2025-08-13 | | Initial release by [@KimPlv](https://github.com/KimPlv) via Connector Builder |

</details>
