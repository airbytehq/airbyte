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
| 0.0.7 | 2025-05-24 | [60599](https://github.com/airbytehq/airbyte/pull/60599) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59847](https://github.com/airbytehq/airbyte/pull/59847) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59364](https://github.com/airbytehq/airbyte/pull/59364) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58685](https://github.com/airbytehq/airbyte/pull/58685) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58232](https://github.com/airbytehq/airbyte/pull/58232) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57639](https://github.com/airbytehq/airbyte/pull/57639) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56993](https://github.com/airbytehq/airbyte/pull/56993) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
