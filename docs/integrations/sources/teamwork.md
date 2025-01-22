# Teamwork

This page contains the setup guide and reference information for the Teamwork source connector.

## Prerequisites

- Teamwork console username
- Teamwork console password

## Documentation reference:
Visit `https://apidocs.teamwork.com/docs/teamwork/v3/` for API documentation

## Authentication setup

Teamwork uses basic http auth that uses username and password
Your default login username and password could be used as secrets, ref: `https://apidocs.teamwork.com/guides/teamwork/authentication`


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username.  |  |
| `password` | `string` | Password.  |  |
| `site_name` | `string` | Site Name. The teamwork site name which appears on the url |  |
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

| Version | Date | Pull Request | Subject |
| ------------------ | ------------ | --- | ---------------- |
| 0.0.10 | 2025-01-18 | [51988](https://github.com/airbytehq/airbyte/pull/51988) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51399](https://github.com/airbytehq/airbyte/pull/51399) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50758](https://github.com/airbytehq/airbyte/pull/50758) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50362](https://github.com/airbytehq/airbyte/pull/50362) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49757](https://github.com/airbytehq/airbyte/pull/49757) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49429](https://github.com/airbytehq/airbyte/pull/49429) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49119](https://github.com/airbytehq/airbyte/pull/49119) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48149](https://github.com/airbytehq/airbyte/pull/48149) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47552](https://github.com/airbytehq/airbyte/pull/47552) | Update dependencies |
| 0.0.1 | 2024-09-05 | [45155](https://github.com/airbytehq/airbyte/pull/45155) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
