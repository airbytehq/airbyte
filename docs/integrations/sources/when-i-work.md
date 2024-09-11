# When_i_work
This page contains the setup guide and reference information for the [When I Work](https://wheniwork.com/) source connector.
Website: 

## Documentation reference:
Visit `https://apidocs.wheniwork.com/external/index.html` for API documentation

## Authentication setup
`When I work` uses bearer token authentication,
Refer `https://apidocs.wheniwork.com/external/index.html?repo=login` for more details.

## Getting token via postman
Make a POST call to URL `https://api.login.wheniwork.com/login`
Along with body as raw-json with your login email and password
```bash
{
  "email": "xxxx@yyyy.com",
  "password": "123456789"
}
```
You will get a response containing token for your authentication.

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

| Version          | Date       |PR| Subject        |
|------------------|------------|---|----------------|
| 0.0.1 | 2024-09-10 |[45367](https://github.com/airbytehq/airbyte/pull/45367)| Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>