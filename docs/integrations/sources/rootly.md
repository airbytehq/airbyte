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
| 0.0.1 | 2024-10-09 | [46669](https://github.com/airbytehq/airbyte/pull/46669) | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
