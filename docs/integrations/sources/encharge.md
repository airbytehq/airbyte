# Encharge
The Airbyte connector for [Encharge](https://encharge.io/) enables seamless data integration between Encharge and your data warehouse or other destinations. With this connector, you can easily sync marketing automation data from Encharge. This allows for improved data-driven decision-making and enhanced marketing insights across platforms.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| peoples | id | DefaultPaginator | ✅ |  ❌  |
| accounts | accountId | DefaultPaginator | ✅ |  ❌  |
| account_tags | tag | DefaultPaginator | ✅ |  ❌  |
| segments | id | DefaultPaginator | ✅ |  ❌  |
| fields | name | DefaultPaginator | ✅ |  ❌  |
| schemas | name | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
