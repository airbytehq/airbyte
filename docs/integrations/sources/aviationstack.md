# Aviationstack
Website: https://aviationstack.com/dashboard
API Reference: https://aviationstack.com/documentation

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_key` | `string` | Access Key. Your unique API key for authenticating with the Aviation API. You can find it in your Aviation account dashboard at https://aviationstack.com/dashboard |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| airports | id | DefaultPaginator | ✅ |  ❌  |
| airlines | id | DefaultPaginator | ✅ |  ❌  |
| airplanes | id | DefaultPaginator | ✅ |  ✅  |
| aircraft_types | id | DefaultPaginator | ✅ |  ❌  |
| cities | id | DefaultPaginator | ✅ |  ❌  |
| countries | id | DefaultPaginator | ✅ |  ❌  |
| taxes | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58232](https://github.com/airbytehq/airbyte/pull/58232) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57639](https://github.com/airbytehq/airbyte/pull/57639) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56993](https://github.com/airbytehq/airbyte/pull/56993) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
