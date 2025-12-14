# Mode
This Airbyte connector for Mode allows you to seamlessly sync data between Mode and various destinations, enabling streamlined data analysis and reporting. With this connector, users can extract reports, data models, and other analytics from Mode into their preferred data warehouses or databases, facilitating easier data integration, business intelligence, and advanced analytics workflows. It supports incremental and full data syncs, providing flexibility in data synchronization for Mode users.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use as the username for Basic Authentication. |  |
| `api_secret` | `string` | API Secret. API secret to use as the password for Basic Authentication. |  |
| `workspace` | `string` | workspace.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| groups | token | No pagination | ✅ |  ❌  |
| memberships | member_username | No pagination | ✅ |  ❌  |
| spaces | id | No pagination | ✅ |  ❌  |
| space_memberships | token | No pagination | ✅ |  ❌  |
| groups_memberships | token | No pagination | ✅ |  ❌  |
| data_sources | id | No pagination | ✅ |  ❌  |
| reports | id | No pagination | ✅ |  ❌  |
| report_runs | token | DefaultPaginator | ✅ |  ❌  |
| queries | id | No pagination | ✅ |  ❌  |
| query_runs | id | No pagination | ✅ |  ❌  |
| charts |  | No pagination | ✅ |  ❌  |
| report_filters | id | No pagination | ✅ |  ❌  |
| definitions | id | No pagination | ✅ |  ❌  |
| datasets | token | No pagination | ✅ |  ❌  |
| datasets_runs | token | DefaultPaginator | ✅ |  ❌  |
| field_descriptions |  | DefaultPaginator | ✅ |  ❌  |
| report_schedules | token | No pagination | ✅ |  ❌  |
| reports_subscriptions |  | No pagination | ✅ |  ❌  |
| datasets_schedules | token | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70599](https://github.com/airbytehq/airbyte/pull/70599) | Update dependencies |
| 0.0.40 | 2025-11-25 | [69859](https://github.com/airbytehq/airbyte/pull/69859) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69587](https://github.com/airbytehq/airbyte/pull/69587) | Update dependencies |
| 0.0.38 | 2025-10-29 | [69059](https://github.com/airbytehq/airbyte/pull/69059) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68441](https://github.com/airbytehq/airbyte/pull/68441) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67824](https://github.com/airbytehq/airbyte/pull/67824) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67379](https://github.com/airbytehq/airbyte/pull/67379) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66341](https://github.com/airbytehq/airbyte/pull/66341) | Update dependencies |
| 0.0.33 | 2025-09-09 | [65786](https://github.com/airbytehq/airbyte/pull/65786) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65166](https://github.com/airbytehq/airbyte/pull/65166) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64677](https://github.com/airbytehq/airbyte/pull/64677) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64250](https://github.com/airbytehq/airbyte/pull/64250) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63866](https://github.com/airbytehq/airbyte/pull/63866) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63405](https://github.com/airbytehq/airbyte/pull/63405) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63183](https://github.com/airbytehq/airbyte/pull/63183) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62612](https://github.com/airbytehq/airbyte/pull/62612) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62347](https://github.com/airbytehq/airbyte/pull/62347) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61891](https://github.com/airbytehq/airbyte/pull/61891) | Update dependencies |
| 0.0.23 | 2025-06-14 | [60486](https://github.com/airbytehq/airbyte/pull/60486) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59458](https://github.com/airbytehq/airbyte/pull/59458) | Update dependencies |
| 0.0.21 | 2025-04-27 | [59107](https://github.com/airbytehq/airbyte/pull/59107) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58478](https://github.com/airbytehq/airbyte/pull/58478) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57858](https://github.com/airbytehq/airbyte/pull/57858) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57075](https://github.com/airbytehq/airbyte/pull/57075) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56681](https://github.com/airbytehq/airbyte/pull/56681) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56056](https://github.com/airbytehq/airbyte/pull/56056) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55460](https://github.com/airbytehq/airbyte/pull/55460) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54744](https://github.com/airbytehq/airbyte/pull/54744) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54332](https://github.com/airbytehq/airbyte/pull/54332) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53834](https://github.com/airbytehq/airbyte/pull/53834) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53272](https://github.com/airbytehq/airbyte/pull/53272) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52765](https://github.com/airbytehq/airbyte/pull/52765) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52276](https://github.com/airbytehq/airbyte/pull/52276) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51839](https://github.com/airbytehq/airbyte/pull/51839) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51162](https://github.com/airbytehq/airbyte/pull/51162) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50652](https://github.com/airbytehq/airbyte/pull/50652) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50131](https://github.com/airbytehq/airbyte/pull/50131) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49620](https://github.com/airbytehq/airbyte/pull/49620) | Update dependencies |
| 0.0.3 | 2024-12-12 | [48997](https://github.com/airbytehq/airbyte/pull/48997) | Update dependencies |
| 0.0.2 | 2024-11-04 | [47868](https://github.com/airbytehq/airbyte/pull/47868) | Update dependencies |
| 0.0.1 | 2024-10-12 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
