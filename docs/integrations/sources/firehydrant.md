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

| Version | Date              | Pull Request | Subject        |
|---------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70540](https://github.com/airbytehq/airbyte/pull/70540) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70000](https://github.com/airbytehq/airbyte/pull/70000) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69449](https://github.com/airbytehq/airbyte/pull/69449) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68816](https://github.com/airbytehq/airbyte/pull/68816) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68450](https://github.com/airbytehq/airbyte/pull/68450) | Update dependencies |
| 0.0.36 | 2025-10-14 | [68056](https://github.com/airbytehq/airbyte/pull/68056) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67293](https://github.com/airbytehq/airbyte/pull/67293) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66774](https://github.com/airbytehq/airbyte/pull/66774) | Update dependencies |
| 0.0.33 | 2025-09-24 | [65853](https://github.com/airbytehq/airbyte/pull/65853) | Update dependencies |
| 0.0.32 | 2025-09-05 | [65966](https://github.com/airbytehq/airbyte/pull/65966) | Update to CDK v7.0.0 |
| 0.0.31 | 2025-08-23 | [65275](https://github.com/airbytehq/airbyte/pull/65275) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64699](https://github.com/airbytehq/airbyte/pull/64699) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64358](https://github.com/airbytehq/airbyte/pull/64358) | Update dependencies |
| 0.0.28 | 2025-07-26 | [63989](https://github.com/airbytehq/airbyte/pull/63989) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63589](https://github.com/airbytehq/airbyte/pull/63589) | Update dependencies |
| 0.0.26 | 2025-07-12 | [62956](https://github.com/airbytehq/airbyte/pull/62956) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62798](https://github.com/airbytehq/airbyte/pull/62798) | Update dependencies |
| 0.0.24 | 2025-06-28 | [62410](https://github.com/airbytehq/airbyte/pull/62410) | Update dependencies |
| 0.0.23 | 2025-06-21 | [61939](https://github.com/airbytehq/airbyte/pull/61939) | Update dependencies |
| 0.0.22 | 2025-06-14 | [61278](https://github.com/airbytehq/airbyte/pull/61278) | Update dependencies |
| 0.0.21 | 2025-05-24 | [60430](https://github.com/airbytehq/airbyte/pull/60430) | Update dependencies |
| 0.0.20 | 2025-05-10 | [59388](https://github.com/airbytehq/airbyte/pull/59388) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58327](https://github.com/airbytehq/airbyte/pull/58327) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57811](https://github.com/airbytehq/airbyte/pull/57811) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57265](https://github.com/airbytehq/airbyte/pull/57265) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56536](https://github.com/airbytehq/airbyte/pull/56536) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55954](https://github.com/airbytehq/airbyte/pull/55954) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55315](https://github.com/airbytehq/airbyte/pull/55315) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54938](https://github.com/airbytehq/airbyte/pull/54938) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54432](https://github.com/airbytehq/airbyte/pull/54432) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53746](https://github.com/airbytehq/airbyte/pull/53746) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53336](https://github.com/airbytehq/airbyte/pull/53336) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52812](https://github.com/airbytehq/airbyte/pull/52812) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52356](https://github.com/airbytehq/airbyte/pull/52356) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51635](https://github.com/airbytehq/airbyte/pull/51635) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51117](https://github.com/airbytehq/airbyte/pull/51117) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50544](https://github.com/airbytehq/airbyte/pull/50544) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50022](https://github.com/airbytehq/airbyte/pull/50022) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49520](https://github.com/airbytehq/airbyte/pull/49520) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49205](https://github.com/airbytehq/airbyte/pull/49205) | Update dependencies |
| 0.0.1   | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
