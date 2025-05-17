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
| 0.0.26 | 2025-05-17 | [60584](https://github.com/airbytehq/airbyte/pull/60584) | Update dependencies |
| 0.0.25 | 2025-05-11 | [60207](https://github.com/airbytehq/airbyte/pull/60207) | Update dependencies |
| 0.0.24 | 2025-05-04 | [59597](https://github.com/airbytehq/airbyte/pull/59597) | Update dependencies |
| 0.0.23 | 2025-04-27 | [58986](https://github.com/airbytehq/airbyte/pull/58986) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58420](https://github.com/airbytehq/airbyte/pull/58420) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57955](https://github.com/airbytehq/airbyte/pull/57955) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57294](https://github.com/airbytehq/airbyte/pull/57294) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56765](https://github.com/airbytehq/airbyte/pull/56765) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56191](https://github.com/airbytehq/airbyte/pull/56191) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55531](https://github.com/airbytehq/airbyte/pull/55531) | Update dependencies |
| 0.0.16 | 2025-03-01 | [55012](https://github.com/airbytehq/airbyte/pull/55012) | Update dependencies |
| 0.0.15 | 2025-02-23 | [54604](https://github.com/airbytehq/airbyte/pull/54604) | Update dependencies |
| 0.0.14 | 2025-02-15 | [54004](https://github.com/airbytehq/airbyte/pull/54004) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53502](https://github.com/airbytehq/airbyte/pull/53502) | Update dependencies |
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
