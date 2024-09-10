# When_i_work
Website: https://wheniwork.com/
Auth page: https://apidocs.wheniwork.com/external/index.html?repo=login
API Docs: https://apidocs.wheniwork.com/external/index.html

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account | id | DefaultPaginator | ✅ |  ❌  |
| payrolls | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| timezones | id | No pagination | ✅ |  ❌  |
| payrolls_notices |  | No pagination | ✅ |  ❌  |
| times |  | No pagination | ✅ |  ❌  |
| requests |  | DefaultPaginator | ✅ |  ❌  |
| blocks |  | DefaultPaginator | ✅ |  ❌  |
| sites | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| positions | id | No pagination | ✅ |  ❌  |
| openshiftapprovalrequests |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-10 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>