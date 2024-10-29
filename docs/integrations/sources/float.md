# Float
Float.com enables teams to plan and allocate resources effectively, manage team availability, and track project timelines. This connector automates the data flow between Float and other platforms, ensuring that resource schedules and project plans are up-to-date across all tools you use.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Float Access Token. API token obtained from your Float Account Settings page |  |
| `start_date` | `datetime` | Start Date. | |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | account_id | DefaultPaginator | ✅ |  ❌  |
| departments | department_id | DefaultPaginator | ✅ |  ❌  |
| people | people_id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| public_holidays | id | DefaultPaginator | ✅ |  ❌  |
| holidays | holiday_id | DefaultPaginator | ✅ |  ❌  |
| projects | project_id | DefaultPaginator | ✅ |  ❌  |
| status | status_id | DefaultPaginator | ✅ |  ❌  |
| time_off | timeoff_id | DefaultPaginator | ✅ |  ❌  |
| timeoff-types | timeoff_type_id | DefaultPaginator | ✅ |  ❌  |
| clients | client_id | DefaultPaginator | ✅ |  ❌  |
| phases | phase_id | DefaultPaginator | ✅ |  ❌  |
| project-tasks | task_meta_id | DefaultPaginator | ✅ |  ❌  |
| milestones | milestone_id | DefaultPaginator | ✅ |  ❌  |
| tasks | task_id | DefaultPaginator | ✅ |  ❌  |
| logged-time | logged_time_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-23 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
