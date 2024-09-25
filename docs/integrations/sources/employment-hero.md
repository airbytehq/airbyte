# Employment-Hero
Website: https://secure.employmenthero.com/
API Docs: https://developer.employmenthero.com/api-references/#icon-book-open-introduction
Auth Docs: https://developer.employmenthero.com/api-references/#obtain-access-token
Auth keys: https://secure.employmenthero.com/app/v2/organisations/xxxxx/developer_portal/api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `organization_configids` | `array` | Organization ID. Organization ID which could be found as result of `organizations` stream to be used in other substreams |  |
| `employees_configids` | `array` | Employees ID. Employees IDs in the given organisation found in `employees` stream for passing to sub-streams |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organisations | id | DefaultPaginator | ✅ |  ❌  |
| employees | id | DefaultPaginator | ✅ |  ❌  |
| leave_requests | id | DefaultPaginator | ✅ |  ❌  |
| employee_certifications | id | DefaultPaginator | ✅ |  ❌  |
| pay_details | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| policies | id | DefaultPaginator | ✅ |  ❌  |
| certifications | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| employee_custom_fields | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-25 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>