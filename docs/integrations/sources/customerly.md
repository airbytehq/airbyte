# Customerly
Connector for customerly.io

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | user_id.email | DefaultPaginator | ✅ |  ✅  |
| leads | crmhero_user_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-06-14 | [61282](https://github.com/airbytehq/airbyte/pull/61282) | Update dependencies |
| 0.0.10 | 2025-05-24 | [60372](https://github.com/airbytehq/airbyte/pull/60372) | Update dependencies |
| 0.0.9 | 2025-05-10 | [59995](https://github.com/airbytehq/airbyte/pull/59995) | Update dependencies |
| 0.0.8 | 2025-05-03 | [59409](https://github.com/airbytehq/airbyte/pull/59409) | Update dependencies |
| 0.0.7 | 2025-04-26 | [58839](https://github.com/airbytehq/airbyte/pull/58839) | Update dependencies |
| 0.0.6 | 2025-04-19 | [58358](https://github.com/airbytehq/airbyte/pull/58358) | Update dependencies |
| 0.0.5 | 2025-04-12 | [57803](https://github.com/airbytehq/airbyte/pull/57803) | Update dependencies |
| 0.0.4 | 2025-04-05 | [57256](https://github.com/airbytehq/airbyte/pull/57256) | Update dependencies |
| 0.0.3 | 2025-03-29 | [56518](https://github.com/airbytehq/airbyte/pull/56518) | Update dependencies |
| 0.0.2 | 2025-03-22 | [55940](https://github.com/airbytehq/airbyte/pull/55940) | Update dependencies |
| 0.0.1 | 2025-03-18 | | Initial release by [@Shuky](https://github.com/Shuky) via Connector Builder |

</details>
