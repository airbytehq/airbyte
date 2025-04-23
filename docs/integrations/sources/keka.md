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
| 0.0.10 | 2025-04-19 | [58156](https://github.com/airbytehq/airbyte/pull/58156) | Update dependencies |
| 0.0.9 | 2025-04-12 | [57690](https://github.com/airbytehq/airbyte/pull/57690) | Update dependencies |
| 0.0.8 | 2025-04-05 | [57093](https://github.com/airbytehq/airbyte/pull/57093) | Update dependencies |
| 0.0.7 | 2025-03-29 | [56700](https://github.com/airbytehq/airbyte/pull/56700) | Update dependencies |
| 0.0.6 | 2025-03-22 | [55498](https://github.com/airbytehq/airbyte/pull/55498) | Update dependencies |
| 0.0.5 | 2025-03-01 | [54766](https://github.com/airbytehq/airbyte/pull/54766) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54328](https://github.com/airbytehq/airbyte/pull/54328) | Update dependencies |
| 0.0.3 | 2025-02-15 | [53861](https://github.com/airbytehq/airbyte/pull/53861) | Update dependencies |
| 0.0.2 | 2025-02-08 | [53271](https://github.com/airbytehq/airbyte/pull/53271) | Update dependencies |
| 0.0.1 | 2025-01-29 | | Initial release by [@bhushan-dhwaniris](https://github.com/bhushan-dhwaniris) via Connector Builder |

</details>
