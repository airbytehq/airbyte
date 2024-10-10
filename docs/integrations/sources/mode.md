# Mode
The Airbyte connector for Mode allows you to seamlessly sync data between Mode and various destinations, enabling streamlined data analysis and reporting. With this connector, users can extract reports, data models, and other analytics from Mode into their preferred data warehouses or databases, facilitating easier data integration, business intelligence, and advanced analytics workflows. It supports incremental and full data syncs, providing flexibility in data synchronization for Mode users.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use as the username for Basic Authentication. |  |
| `workspace` | `string` | workspace.  |  |
| `api_secret` | `string` | API Secret. API secret to use as the password for Basic Authentication. |  |

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
| report_schedules |  | DefaultPaginator | ✅ |  ❌  |
| reports_subscriptions |  | No pagination | ✅ |  ❌  |
| datasets_schedules | token | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-10 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
