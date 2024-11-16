# GreytHR
The GreytHR Connector for Airbyte allows seamless integration with the GreytHR platform, enabling users to automate the extraction and synchronization of employee management and payroll data into their preferred destinations for reporting, analytics, or further processing.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `gthost` | `string` | Host URL. Your GreytHR Host URL |  |
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Employees | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employees Categories | employeeId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-16 | | Initial release by [@bhushan-dhwaniris](https://github.com/bhushan-dhwaniris) via Connector Builder |

</details>
