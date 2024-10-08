# When_i_work
This page contains the setup guide and reference information for the [When I Work](https://wheniwork.com/) source connector.

## Documentation reference:
Visit `https://apidocs.wheniwork.com/external/index.html` for API documentation

## Authentication setup
`When I work` uses session token authentication,
You have to give your login email and password used with `when-i-work` account for authentication.
`https://apidocs.wheniwork.com/external/index.html?repo=login`

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
| payrolls_notices | uid | No pagination | ✅ |  ❌  |
| times | uid | No pagination | ✅ |  ❌  |
| requests | id | DefaultPaginator | ✅ |  ❌  |
| blocks | id | DefaultPaginator | ✅ |  ❌  |
| sites | id | DefaultPaginator | ✅ |  ❌  |
| locations | id | DefaultPaginator | ✅ |  ❌  |
| positions | id | No pagination | ✅ |  ❌  |
| openshiftapprovalrequests | uid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.1 | 2024-09-10 | [45367](https://github.com/airbytehq/airbyte/pull/45367) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>