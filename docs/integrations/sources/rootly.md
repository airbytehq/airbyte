# Rootly
## Overview

The Rootly source supports _Full Refresh_ as well as _Incremental_ syncs.
Documentation: https://rootly.com/api#/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| dashboards | id | DefaultPaginator | ✅ |  ✅  |
| incidents | id | DefaultPaginator | ✅ |  ✅  |
| authorizations | id | DefaultPaginator | ✅ |  ✅  |
| dashboards_panels | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| incident_types | id | DefaultPaginator | ✅ |  ✅  |
| ip_ranges | id | DefaultPaginator | ✅ |  ❌  |
| users_notification_rules | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ✅  |
| sub_statuses | id | DefaultPaginator | ✅ |  ✅  |
| incidents_sub_statuses | id | DefaultPaginator | ✅ |  ✅  |
| incident_roles | id | DefaultPaginator | ✅ |  ✅  |
| post_mortems | id | DefaultPaginator | ✅ |  ✅  |
| status-pages | id | DefaultPaginator | ✅ |  ✅  |
| severities | id | DefaultPaginator | ✅ |  ✅  |
| services | id | DefaultPaginator | ✅ |  ✅  |
| incident_permission_sets | id | DefaultPaginator | ✅ |  ✅  |
| incident_permission_sets_resources | id | DefaultPaginator | ✅ |  ✅  |
| incident_permission_sets_booleans | id | DefaultPaginator | ✅ |  ✅  |
| roles | id | DefaultPaginator | ✅ |  ✅  |
| incidents_events | id | DefaultPaginator | ✅ |  ✅  |
| workflows | id | DefaultPaginator | ✅ |  ✅  |
| workflow_groups | id | DefaultPaginator | ✅ |  ✅  |
| workflows_tasks | id | DefaultPaginator | ✅ |  ✅  |
| form_sets | id | DefaultPaginator | ✅ |  ✅  |
| form_fields | id | DefaultPaginator | ✅ |  ✅  |
| playbooks | id | DefaultPaginator | ✅ |  ✅  |
| incidents_action_items | id | DefaultPaginator | ✅ |  ✅  |
| retrospective_configurations | id | DefaultPaginator | ✅ |  ✅  |
| retrospective_processes | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.12 | 2025-02-01 | [53017](https://github.com/airbytehq/airbyte/pull/53017) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52484](https://github.com/airbytehq/airbyte/pull/52484) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51851](https://github.com/airbytehq/airbyte/pull/51851) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51301](https://github.com/airbytehq/airbyte/pull/51301) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50735](https://github.com/airbytehq/airbyte/pull/50735) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50262](https://github.com/airbytehq/airbyte/pull/50262) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49717](https://github.com/airbytehq/airbyte/pull/49717) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49355](https://github.com/airbytehq/airbyte/pull/49355) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49063](https://github.com/airbytehq/airbyte/pull/49063) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48240](https://github.com/airbytehq/airbyte/pull/48240) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47833](https://github.com/airbytehq/airbyte/pull/47833) | Update dependencies |
| 0.0.1 | 2024-10-09 | [46669](https://github.com/airbytehq/airbyte/pull/46669) | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
