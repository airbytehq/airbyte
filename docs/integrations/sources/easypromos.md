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
| 0.0.4 | 2024-12-14 | [49477](https://github.com/airbytehq/airbyte/pull/49477) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49180](https://github.com/airbytehq/airbyte/pull/49180) | Update dependencies |
| 0.0.2 | 2024-11-04 | [48302](https://github.com/airbytehq/airbyte/pull/48302) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
