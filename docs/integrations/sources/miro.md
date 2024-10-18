# Miro
Airbyte connector, Miro&#39;s API could be used to extract data related to board content, user activities, and collaboration metrics, enabling integration with data warehouses and further analysis of team interactions and productivity.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| boards | id | DefaultPaginator | ✅ |  ❌  |
| board_users |  | DefaultPaginator | ✅ |  ❌  |
| board_items |  | DefaultPaginator | ✅ |  ❌  |
| tags |  | No pagination | ✅ |  ❌  |
| groups |  | No pagination | ✅ |  ❌  |
| connectors | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-18 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
