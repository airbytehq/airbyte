# FireHydrant
The Airbyte connector for FireHydrant enables seamless data integration between FireHydrant and your data ecosystem. It allows you to efficiently extract incident management and reliability data from FireHydrant, empowering teams with valuable insights for post-incident analysis, reliability reporting, and proactive system monitoring. With this connector, users can automate the data flow and gain deeper visibility into incidents and response metrics, improving reliability and operational efficiency.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Bot token to use for authenticating with the FireHydrant API. You can find or create a bot token by logging into your organization and visiting the Bot users page at https://app.firehydrant.io/organizations/bots. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| enviroments | id | DefaultPaginator | ✅ |  ❌  |
| services | id | DefaultPaginator | ✅ |  ❌  |
| functionalities | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |
| signals_on_call | id | DefaultPaginator | ✅ |  ❌  |
| changes_events | id | DefaultPaginator | ✅ |  ❌  |
| changes | id | DefaultPaginator | ✅ |  ❌  |
| entitlements | slug | No pagination | ✅ |  ❌  |
| incidents | id | DefaultPaginator | ✅ |  ❌  |
| incident_roles | id | DefaultPaginator | ✅ |  ❌  |
| incident_tags | name | DefaultPaginator | ✅ |  ❌  |
| incident_types | id | DefaultPaginator | ✅ |  ❌  |
| integrations | id | No pagination | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| reports | bucket | No pagination | ✅ |  ❌  |
| runbook_actions | id | DefaultPaginator | ✅ |  ❌  |
| runbook_executions | id | DefaultPaginator | ✅ |  ❌  |
| runbooks | id | DefaultPaginator | ✅ |  ❌  |
| runbook_audits | id | DefaultPaginator | ✅ |  ❌  |
| nunc_connections | id | DefaultPaginator | ✅ |  ❌  |
| measurement_definitions | id | DefaultPaginator | ✅ |  ❌  |
| phases | id | No pagination | ✅ |  ❌  |
| priorities | slug | DefaultPaginator | ✅ |  ❌  |
| severities | slug | DefaultPaginator | ✅ |  ❌  |
| severity_matrix_conditions | id | DefaultPaginator | ✅ |  ❌  |
| severity_matrix_impacts | id | DefaultPaginator | ✅ |  ❌  |
| scheduled_maintenances | id | DefaultPaginator | ✅ |  ❌  |
| infrastructures | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields_definitions | field_id | No pagination | ✅ |  ❌  |
| post_mortems_reports | id | DefaultPaginator | ✅ |  ❌  |
| post_mortems_questions | id | DefaultPaginator | ✅ |  ❌  |
| alerts | id | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |
| ticketing_projects | id | DefaultPaginator | ✅ |  ❌  |
| ticketing_priorities | id | No pagination | ✅ |  ❌  |
| ticket_tags | name | DefaultPaginator | ✅ |  ❌  |
| task_lists | id | DefaultPaginator | ✅ |  ❌  |
| checklist_templates | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2025-01-18 | [51635](https://github.com/airbytehq/airbyte/pull/51635) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51117](https://github.com/airbytehq/airbyte/pull/51117) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50544](https://github.com/airbytehq/airbyte/pull/50544) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50022](https://github.com/airbytehq/airbyte/pull/50022) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49520](https://github.com/airbytehq/airbyte/pull/49520) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49205](https://github.com/airbytehq/airbyte/pull/49205) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
