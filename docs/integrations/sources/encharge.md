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
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
