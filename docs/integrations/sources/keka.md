# Keka
The Keka Connector for Airbyte allows seamless integration with the Keka platform, enabling users to automate the extraction and synchronization of employee management and payroll data into their preferred destinations for reporting, analytics, or further processing.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `scope` | `string` | Scope.  |  |
| `api_key` | `string` | API Key.  |  |
| `client_id` | `string` | Client ID. Your client identifier for authentication. |  |
| `grant_type` | `string` | Grant Type.  |  |
| `client_secret` | `string` | Client Secret. Your client secret for secure authentication. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Employees |  | DefaultPaginator | ✅ |  ❌  |
| Attendance |  | DefaultPaginator | ✅ |  ❌  |
| Clients |  | DefaultPaginator | ✅ |  ❌  |
| Projects |  | DefaultPaginator | ✅ |  ❌  |
| Project Timesheets |  | DefaultPaginator | ✅ |  ❌  |
| Leave Type | identifier | DefaultPaginator | ✅ |  ❌  |
| Leave Request |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-01-29 | | Initial release by [@bhushan-dhwaniris](https://github.com/bhushan-dhwaniris) via Connector Builder |

</details>
