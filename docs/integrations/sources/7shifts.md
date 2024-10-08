# 7shifts
7shifts is a scheduling, payroll, and employee retention app designed to improve performance for restaurants.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. Access token to use for authentication. Generate it in the 7shifts Developer Tools. |  |
| `start_date` | `string` | Start date.  |  |

Generate an Access Token by navigating to "Company Settings", then "Developer Tools". Under the Access Token Section click "Create Access Token". See [here](https://developers.7shifts.com/reference/authentication#creating-access-tokens) for more details.

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| companies | id | DefaultPaginator | ✅ |  ✅  |
| locations | id | DefaultPaginator | ✅ |  ✅  |
| departments | id | DefaultPaginator | ✅ |  ✅  |
| roles | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| wages |  | No pagination | ✅ |  ❌  |
| assignments |  | No pagination | ✅ |  ❌  |
| location_assignments |  | No pagination | ✅ |  ❌  |
| department_assignments |  | No pagination | ✅ |  ❌  |
| role_assignments |  | No pagination | ✅ |  ❌  |
| time_punches | id | DefaultPaginator | ✅ |  ✅  |
| shifts | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-18 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>