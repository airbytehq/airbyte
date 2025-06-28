# Jira Service Management
Airbyte connector for Jira Service Management (JSM), a separate application from Jira Software. This connector enables data extraction from JSM-specific entities such as assets.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `password` | `string` | Password.  |  |
| `username` | `string` | Username.  |  |
| `start_date` | `string` | Start date.  |  |
| `workspace_id` | `string` | Workspace ID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| assets | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-06-27 | | Initial release by [@akaloshych84](https://github.com/akaloshych84) via Connector Builder |

</details>
