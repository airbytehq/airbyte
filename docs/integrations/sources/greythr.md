# GreytHr
The GreytHR Connector for Airbyte allows seamless integration with the GreytHR platform, enabling users to automate the extraction and synchronization of employee management and payroll data into their preferred destinations for reporting, analytics, or further processing.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `domain` | `string` | Host URL. Your GreytHR Host URL |  |
| `base_url` | `string` | Base URL. https://api.greythr.com |  |
| `password` | `string` | Password.  |  |
| `username` | `string` | Username.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Employees | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employees Categories | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employees Profile | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employees Personal Details | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employees Work Details | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employee Separation Details | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employee Statutory Details | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employee Bank Details | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employee PF &amp; ESI details | employeeId | DefaultPaginator | ✅ |  ❌  |
| Employee Qualifications Details |  | DefaultPaginator | ✅ |  ❌  |
| Users List |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2024-12-14 | [49621](https://github.com/airbytehq/airbyte/pull/49621) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48920](https://github.com/airbytehq/airbyte/pull/48920) | Update dependencies |
| 0.0.1 | 2024-11-29 | | Initial release by [@bhushan-dhwaniris](https://github.com/bhushan-dhwaniris) via Connector Builder |

</details>
