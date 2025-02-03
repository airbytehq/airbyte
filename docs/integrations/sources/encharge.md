# Encharge
Airbyte connector for [Encharge](https://encharge.io/) enables seamless data integration between Encharge and your data warehouse or other destinations. With this connector, you can easily sync marketing automation data from Encharge. This allows for improved data-driven decision-making and enhanced marketing insights across platforms.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| peoples | id | DefaultPaginator | ✅ |  ❌  |
| accounts | accountId | No pagination | ✅ |  ❌  |
| account_tags | tag | No pagination | ✅ |  ❌  |
| segments | id | DefaultPaginator | ✅ |  ❌  |
| segment_people | id | DefaultPaginator | ✅ |  ❌  |
| fields | name | No pagination | ✅ |  ❌  |
| schemas | name | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-02-01 | [52810](https://github.com/airbytehq/airbyte/pull/52810) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52327](https://github.com/airbytehq/airbyte/pull/52327) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51708](https://github.com/airbytehq/airbyte/pull/51708) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51115](https://github.com/airbytehq/airbyte/pull/51115) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50537](https://github.com/airbytehq/airbyte/pull/50537) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50001](https://github.com/airbytehq/airbyte/pull/50001) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49509](https://github.com/airbytehq/airbyte/pull/49509) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49175](https://github.com/airbytehq/airbyte/pull/49175) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
