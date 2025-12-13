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
| 0.0.19 | 2025-12-09 | [70805](https://github.com/airbytehq/airbyte/pull/70805) | Update dependencies |
| 0.0.18 | 2025-11-25 | [69861](https://github.com/airbytehq/airbyte/pull/69861) | Update dependencies |
| 0.0.17 | 2025-11-18 | [69574](https://github.com/airbytehq/airbyte/pull/69574) | Update dependencies |
| 0.0.16 | 2025-10-29 | [68842](https://github.com/airbytehq/airbyte/pull/68842) | Update dependencies |
| 0.0.15 | 2025-10-21 | [68359](https://github.com/airbytehq/airbyte/pull/68359) | Update dependencies |
| 0.0.14 | 2025-10-14 | [67966](https://github.com/airbytehq/airbyte/pull/67966) | Update dependencies |
| 0.0.13 | 2025-10-07 | [67165](https://github.com/airbytehq/airbyte/pull/67165) | Update dependencies |
| 0.0.12 | 2025-09-30 | [66274](https://github.com/airbytehq/airbyte/pull/66274) | Update dependencies |
| 0.0.11 | 2025-09-09 | [66037](https://github.com/airbytehq/airbyte/pull/66037) | Update dependencies |
| 0.0.10 | 2025-08-02 | [64407](https://github.com/airbytehq/airbyte/pull/64407) | Update dependencies |
| 0.0.9 | 2025-07-12 | [63058](https://github.com/airbytehq/airbyte/pull/63058) | Update dependencies |
| 0.0.8 | 2025-06-28 | [61445](https://github.com/airbytehq/airbyte/pull/61445) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60599](https://github.com/airbytehq/airbyte/pull/60599) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59847](https://github.com/airbytehq/airbyte/pull/59847) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59364](https://github.com/airbytehq/airbyte/pull/59364) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58685](https://github.com/airbytehq/airbyte/pull/58685) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58232](https://github.com/airbytehq/airbyte/pull/58232) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57639](https://github.com/airbytehq/airbyte/pull/57639) | Update dependencies |
| 0.0.1 | 2025-04-03 | [56993](https://github.com/airbytehq/airbyte/pull/56993) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
