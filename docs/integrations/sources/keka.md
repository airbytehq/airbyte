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
| 0.0.30 | 2025-12-09 | [70772](https://github.com/airbytehq/airbyte/pull/70772) | Update dependencies |
| 0.0.29 | 2025-11-25 | [69502](https://github.com/airbytehq/airbyte/pull/69502) | Update dependencies |
| 0.0.28 | 2025-10-29 | [68521](https://github.com/airbytehq/airbyte/pull/68521) | Update dependencies |
| 0.0.27 | 2025-10-14 | [67974](https://github.com/airbytehq/airbyte/pull/67974) | Update dependencies |
| 0.0.26 | 2025-10-07 | [67355](https://github.com/airbytehq/airbyte/pull/67355) | Update dependencies |
| 0.0.25 | 2025-09-30 | [66804](https://github.com/airbytehq/airbyte/pull/66804) | Update dependencies |
| 0.0.24 | 2025-09-09 | [66103](https://github.com/airbytehq/airbyte/pull/66103) | Update dependencies |
| 0.0.23 | 2025-08-23 | [65386](https://github.com/airbytehq/airbyte/pull/65386) | Update dependencies |
| 0.0.22 | 2025-08-09 | [64621](https://github.com/airbytehq/airbyte/pull/64621) | Update dependencies |
| 0.0.21 | 2025-08-02 | [64243](https://github.com/airbytehq/airbyte/pull/64243) | Update dependencies |
| 0.0.20 | 2025-07-26 | [63908](https://github.com/airbytehq/airbyte/pull/63908) | Update dependencies |
| 0.0.19 | 2025-07-19 | [63459](https://github.com/airbytehq/airbyte/pull/63459) | Update dependencies |
| 0.0.18 | 2025-07-12 | [63145](https://github.com/airbytehq/airbyte/pull/63145) | Update dependencies |
| 0.0.17 | 2025-07-05 | [62645](https://github.com/airbytehq/airbyte/pull/62645) | Update dependencies |
| 0.0.16 | 2025-06-28 | [62172](https://github.com/airbytehq/airbyte/pull/62172) | Update dependencies |
| 0.0.15 | 2025-06-21 | [61849](https://github.com/airbytehq/airbyte/pull/61849) | Update dependencies |
| 0.0.14 | 2025-06-14 | [61129](https://github.com/airbytehq/airbyte/pull/61129) | Update dependencies |
| 0.0.13 | 2025-05-24 | [59800](https://github.com/airbytehq/airbyte/pull/59800) | Update dependencies |
| 0.0.12 | 2025-05-03 | [59247](https://github.com/airbytehq/airbyte/pull/59247) | Update dependencies |
| 0.0.11 | 2025-04-26 | [58796](https://github.com/airbytehq/airbyte/pull/58796) | Update dependencies |
| 0.0.10 | 2025-04-19 | [58156](https://github.com/airbytehq/airbyte/pull/58156) | Update dependencies |
| 0.0.9 | 2025-04-12 | [57690](https://github.com/airbytehq/airbyte/pull/57690) | Update dependencies |
| 0.0.8 | 2025-04-05 | [57093](https://github.com/airbytehq/airbyte/pull/57093) | Update dependencies |
| 0.0.7 | 2025-03-29 | [56700](https://github.com/airbytehq/airbyte/pull/56700) | Update dependencies |
| 0.0.6 | 2025-03-22 | [55498](https://github.com/airbytehq/airbyte/pull/55498) | Update dependencies |
| 0.0.5 | 2025-03-01 | [54766](https://github.com/airbytehq/airbyte/pull/54766) | Update dependencies |
| 0.0.4 | 2025-02-22 | [54328](https://github.com/airbytehq/airbyte/pull/54328) | Update dependencies |
| 0.0.3 | 2025-02-15 | [53861](https://github.com/airbytehq/airbyte/pull/53861) | Update dependencies |
| 0.0.2 | 2025-02-08 | [53271](https://github.com/airbytehq/airbyte/pull/53271) | Update dependencies |
| 0.0.1 | 2025-01-29 | | Initial release by [@bhushan-barbuddhe](https://github.com/bhushan-barbuddhe) via Connector Builder |

</details>
