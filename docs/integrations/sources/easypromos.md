# Easypromos
Airbyte connector for [Easypromos](https://www.easypromosapp.com/) enables seamless data extraction from Easypromos, an online platform for running contests, giveaways, and promotions. It facilitates automatic syncing of participant information, promotion performance, and engagement metrics into data warehouses, streamlining analytics and reporting. This integration helps businesses easily analyze campaign data and optimize marketing strategies

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `bearer_token` | `string` | Bearer Token.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| promotions | id | DefaultPaginator | ✅ |  ❌  |
| organizing_brands | id | DefaultPaginator | ✅ |  ❌  |
| stages | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| participations | id | DefaultPaginator | ✅ |  ❌  |
| prizes | id | DefaultPaginator | ✅ |  ❌  |
| rankings | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-02-08 | [53381](https://github.com/airbytehq/airbyte/pull/53381) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52846](https://github.com/airbytehq/airbyte/pull/52846) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52333](https://github.com/airbytehq/airbyte/pull/52333) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51626](https://github.com/airbytehq/airbyte/pull/51626) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51089](https://github.com/airbytehq/airbyte/pull/51089) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50586](https://github.com/airbytehq/airbyte/pull/50586) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50003](https://github.com/airbytehq/airbyte/pull/50003) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49477](https://github.com/airbytehq/airbyte/pull/49477) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49180](https://github.com/airbytehq/airbyte/pull/49180) | Update dependencies |
| 0.0.2 | 2024-11-04 | [48302](https://github.com/airbytehq/airbyte/pull/48302) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
