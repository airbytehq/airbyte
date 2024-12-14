# Segment
Connector that pulls from Segment&#39;s Public API.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `region` | `string` | Region. The region for the API, e.g., &#39;api&#39; for US or &#39;eu1&#39; for EU | api |
| `api_token` | `string` | API Token. API token to use. Generate it in Segment&#39;s Workspace settings. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| warehouses | id | DefaultPaginator | ✅ |  ❌  |
| sources | id | DefaultPaginator | ✅ |  ❌  |
| destinations | id | DefaultPaginator | ✅ |  ❌  |
| reverse_etl_models | id | DefaultPaginator | ✅ |  ❌  |
| catalog_destinations | id | DefaultPaginator | ✅ |  ❌  |
| catalog_sources | id | DefaultPaginator | ✅ |  ❌  |
| catalog_warehouses | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| labels | key.value | DefaultPaginator | ✅ |  ❌  |
| audit_events | id | DefaultPaginator | ✅ |  ❌  |
| transformations | id | DefaultPaginator | ✅ |  ❌  |
| spaces | id | DefaultPaginator | ✅ |  ❌  |
| usage_api_calls_daily | timestamp | DefaultPaginator | ✅ |  ✅  |
| usage_mtu_daily | timestamp | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.5 | 2024-12-14 | [49722](https://github.com/airbytehq/airbyte/pull/49722) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49350](https://github.com/airbytehq/airbyte/pull/49350) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49062](https://github.com/airbytehq/airbyte/pull/49062) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-10-29 | [47546](https://github.com/airbytehq/airbyte/pull/47546) | Update dependencies |
| 0.0.1 | 2024-10-04 | | Initial release by [@zckymc](https://github.com/zckymc) via Connector Builder |

</details>
