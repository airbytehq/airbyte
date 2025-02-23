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
| 0.0.12 | 2025-02-22 | [54402](https://github.com/airbytehq/airbyte/pull/54402) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53710](https://github.com/airbytehq/airbyte/pull/53710) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53364](https://github.com/airbytehq/airbyte/pull/53364) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52797](https://github.com/airbytehq/airbyte/pull/52797) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52377](https://github.com/airbytehq/airbyte/pull/52377) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51647](https://github.com/airbytehq/airbyte/pull/51647) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51067](https://github.com/airbytehq/airbyte/pull/51067) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50552](https://github.com/airbytehq/airbyte/pull/50552) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50033](https://github.com/airbytehq/airbyte/pull/50033) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49476](https://github.com/airbytehq/airbyte/pull/49476) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48211](https://github.com/airbytehq/airbyte/pull/48211) | Update dependencies |
| 0.0.1 | 2024-10-23 | | Initial release by [@bala-ceg](https://github.com/bala-ceg) via Connector Builder |

</details>
