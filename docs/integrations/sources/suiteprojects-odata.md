# SuiteProjects OData
Getting utilization by employee data for BI use

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `password` | `string` | Password.  |  |
| `username` | `string` | Username.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Elixir Charge Projections |  | No pagination | ✅ |  ❌  |
| Projects | Internal id | DefaultPaginator | ✅ |  ❌  |
| ProjectTasksPhases | Internal id | DefaultPaginator | ✅ |  ❌  |
| ProjectSnapshots | Internal id | DefaultPaginator | ✅ |  ❌  |
| Utilization By Employee |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-07-22 | | Initial release by [@gjadhav300](https://github.com/gjadhav300) via Connector Builder |

</details>
