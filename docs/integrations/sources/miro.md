# Miro

Airbyte connector for Miro can be used to extract data related to board content, user activities, and collaboration metrics, enabling integration with data warehouses and further analysis of team interactions and productivity.

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
| board_tags |  | DefaultPaginator | ✅ |  ❌  |
| board_groups |  | No pagination | ✅ |  ❌  |
| board_connectors | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.12 | 2025-02-08 | [53306](https://github.com/airbytehq/airbyte/pull/53306) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52779](https://github.com/airbytehq/airbyte/pull/52779) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52243](https://github.com/airbytehq/airbyte/pull/52243) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51827](https://github.com/airbytehq/airbyte/pull/51827) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51182](https://github.com/airbytehq/airbyte/pull/51182) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50658](https://github.com/airbytehq/airbyte/pull/50658) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50135](https://github.com/airbytehq/airbyte/pull/50135) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49629](https://github.com/airbytehq/airbyte/pull/49629) | Update dependencies |
| 0.0.4 | 2024-12-12 | [48922](https://github.com/airbytehq/airbyte/pull/48922) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48262](https://github.com/airbytehq/airbyte/pull/48262) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47885](https://github.com/airbytehq/airbyte/pull/47885) | Update dependencies |
| 0.0.1 | 2024-10-18 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
