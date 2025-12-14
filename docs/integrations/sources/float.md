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
| 0.0.40 | 2025-12-09 | [70590](https://github.com/airbytehq/airbyte/pull/70590) | Update dependencies |
| 0.0.39 | 2025-11-25 | [69997](https://github.com/airbytehq/airbyte/pull/69997) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69447](https://github.com/airbytehq/airbyte/pull/69447) | Update dependencies |
| 0.0.37 | 2025-10-29 | [68837](https://github.com/airbytehq/airbyte/pull/68837) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68453](https://github.com/airbytehq/airbyte/pull/68453) | Update dependencies |
| 0.0.35 | 2025-10-14 | [68042](https://github.com/airbytehq/airbyte/pull/68042) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67294](https://github.com/airbytehq/airbyte/pull/67294) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66770](https://github.com/airbytehq/airbyte/pull/66770) | Update dependencies |
| 0.0.32 | 2025-09-24 | [65798](https://github.com/airbytehq/airbyte/pull/65798) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65301](https://github.com/airbytehq/airbyte/pull/65301) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64776](https://github.com/airbytehq/airbyte/pull/64776) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64370](https://github.com/airbytehq/airbyte/pull/64370) | Update dependencies |
| 0.0.28 | 2025-07-26 | [63937](https://github.com/airbytehq/airbyte/pull/63937) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63595](https://github.com/airbytehq/airbyte/pull/63595) | Update dependencies |
| 0.0.26 | 2025-07-17 | [63315](https://github.com/airbytehq/airbyte/pull/63315) | source-float contribution from cvd |
| 0.0.25 | 2025-07-12 | [63025](https://github.com/airbytehq/airbyte/pull/63025) | Update dependencies |
| 0.0.24 | 2025-07-05 | [62759](https://github.com/airbytehq/airbyte/pull/62759) | Update dependencies |
| 0.0.23 | 2025-06-28 | [62314](https://github.com/airbytehq/airbyte/pull/62314) | Update dependencies |
| 0.0.22 | 2025-06-21 | [61955](https://github.com/airbytehq/airbyte/pull/61955) | Update dependencies |
| 0.0.21 | 2025-06-14 | [60401](https://github.com/airbytehq/airbyte/pull/60401) | Update dependencies |
| 0.0.20 | 2025-05-10 | [59937](https://github.com/airbytehq/airbyte/pull/59937) | Update dependencies |
| 0.0.19 | 2025-05-03 | [58908](https://github.com/airbytehq/airbyte/pull/58908) | Update dependencies |
| 0.0.18 | 2025-04-19 | [57837](https://github.com/airbytehq/airbyte/pull/57837) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57258](https://github.com/airbytehq/airbyte/pull/57258) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56533](https://github.com/airbytehq/airbyte/pull/56533) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55942](https://github.com/airbytehq/airbyte/pull/55942) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55330](https://github.com/airbytehq/airbyte/pull/55330) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54994](https://github.com/airbytehq/airbyte/pull/54994) | Update dependencies |
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
