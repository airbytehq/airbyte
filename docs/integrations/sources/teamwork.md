# Teamwork
New Source: Teamwork
Authentication Docs: https://apidocs.teamwork.com/guides/teamwork/authentication
API Docs: https://apidocs.teamwork.com/docs/teamwork/v3/
Website: https://www.teamwork.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `site_name` | `string` | Site Name. The teamwork site name appearing at the url |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| latestactivity | id | DefaultPaginator | ✅ |  ✅  |
| projects | id | DefaultPaginator | ✅ |  ✅  |
| projects_active | value | DefaultPaginator | ✅ |  ❌  |
| projects_billable | name | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ✅  |
| me_timers | id | DefaultPaginator | ✅ |  ✅  |
| time_entries | id | DefaultPaginator | ✅ |  ✅  |
| timelog_totals |  | DefaultPaginator | ✅ |  ❌  |
| dashboards | id | DefaultPaginator | ✅ |  ✅  |
| forms | id | DefaultPaginator | ✅ |  ✅  |
| milestones | id | DefaultPaginator | ✅ |  ✅  |
| milestones_deadlines |  | DefaultPaginator | ✅ |  ❌  |
| notebooks | id | DefaultPaginator | ✅ |  ✅  |
| people | id | DefaultPaginator | ✅ |  ❌  |
| notebooks_comments.json | id | DefaultPaginator | ✅ |  ✅  |
| projectcategories | id | DefaultPaginator | ✅ |  ❌  |
| tasklists | id | DefaultPaginator | ✅ |  ✅  |
| tasks | id | DefaultPaginator | ✅ |  ✅  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| timesheets |  | DefaultPaginator | ✅ |  ❌  |
| workload_planners |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-05 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>