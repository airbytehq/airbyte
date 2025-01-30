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
| 0.0.11 | 2025-01-25 | [52175](https://github.com/airbytehq/airbyte/pull/52175) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51725](https://github.com/airbytehq/airbyte/pull/51725) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51241](https://github.com/airbytehq/airbyte/pull/51241) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50494](https://github.com/airbytehq/airbyte/pull/50494) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50183](https://github.com/airbytehq/airbyte/pull/50183) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49575](https://github.com/airbytehq/airbyte/pull/49575) | Update dependencies |
| 0.0.5 | 2024-12-12 | [48964](https://github.com/airbytehq/airbyte/pull/48964) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48174](https://github.com/airbytehq/airbyte/pull/48174) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47829](https://github.com/airbytehq/airbyte/pull/47829) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47575](https://github.com/airbytehq/airbyte/pull/47575) | Update dependencies |
| 0.0.1 | 2024-09-18 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
