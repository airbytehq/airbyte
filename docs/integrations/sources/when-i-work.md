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
| 0.0.8 | 2025-01-11 | [51415](https://github.com/airbytehq/airbyte/pull/51415) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50771](https://github.com/airbytehq/airbyte/pull/50771) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50374](https://github.com/airbytehq/airbyte/pull/50374) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49795](https://github.com/airbytehq/airbyte/pull/49795) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49389](https://github.com/airbytehq/airbyte/pull/49389) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48303](https://github.com/airbytehq/airbyte/pull/48303) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47565](https://github.com/airbytehq/airbyte/pull/47565) | Update dependencies |
| 0.0.1 | 2024-09-10 | [45367](https://github.com/airbytehq/airbyte/pull/45367) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
