# Zoho Desk
This directory contains the manifest-only connector for source-zoho-desk

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `token_refresh_endpoint` | `string` | Token Refresh Endpoint.  |  |
| `refresh_token` | `string` | OAuth Refresh Token.  |  |
| `include_custom_domain` | `boolean` | include Custom Domain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organization | id | No pagination | ✅ |  ❌  |
| all_organizations | id | No pagination | ✅ |  ❌  |
| accessible_organizations |  | No pagination | ✅ |  ❌  |
| agent |  | No pagination | ✅ |  ❌  |
| list_agents | id | DefaultPaginator | ✅ |  ❌  |
| agent_details_by_id | id | No pagination | ✅ |  ❌  |
| profiles | id | No pagination | ✅ |  ❌  |
| list_roles | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| team_members | id | No pagination | ✅ |  ❌  |
| list_departments |  | DefaultPaginator | ✅ |  ❌  |
| channels | code | No pagination | ✅ |  ❌  |
| list_tickets | id | DefaultPaginator | ✅ |  ❌  |
| list_all_threads | id | DefaultPaginator | ✅ |  ❌  |
| get_latest_thread | id | No pagination | ✅ |  ❌  |
| list_contacts | id | DefaultPaginator | ✅ |  ❌  |
| webhooks |  | No pagination | ✅ |  ❌  |
| list_accounts | id | DefaultPaginator | ✅ |  ❌  |
| list_contracts | id | DefaultPaginator | ✅ |  ❌  |
| list_tasks | id | DefaultPaginator | ✅ |  ❌  |
| list_products | id | DefaultPaginator | ✅ |  ❌  |
| list_articles | id | No pagination | ✅ |  ❌  |
| list_events | id | DefaultPaginator | ✅ |  ❌  |
| modules | id | No pagination | ✅ |  ❌  |
| list_users | id | DefaultPaginator | ✅ |  ❌  |
| ticket_activities | id | DefaultPaginator | ✅ |  ❌  |
| list_attachments |  | DefaultPaginator | ✅ |  ❌  |
| product | id | No pagination | ✅ |  ❌  |
| task_attachments | id | DefaultPaginator | ✅ |  ❌  |
| list_calls | id | DefaultPaginator | ✅ |  ❌  |
| call | id | No pagination | ✅ |  ❌  |
| list_call_comments | id | DefaultPaginator | ✅ |  ❌  |
| dashboard_created_tickets |  | No pagination | ✅ |  ❌  |
| list_user_groups | id | DefaultPaginator | ✅ |  ❌  |
| dashboard_onhold_tickets | value | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.40 | 2025-12-09 | [70798](https://github.com/airbytehq/airbyte/pull/70798) | Update dependencies |
| 0.0.39 | 2025-11-25 | [70150](https://github.com/airbytehq/airbyte/pull/70150) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69430](https://github.com/airbytehq/airbyte/pull/69430) | Update dependencies |
| 0.0.37 | 2025-10-29 | [68986](https://github.com/airbytehq/airbyte/pull/68986) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68499](https://github.com/airbytehq/airbyte/pull/68499) | Update dependencies |
| 0.0.35 | 2025-10-14 | [68022](https://github.com/airbytehq/airbyte/pull/68022) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67235](https://github.com/airbytehq/airbyte/pull/67235) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66854](https://github.com/airbytehq/airbyte/pull/66854) | Update dependencies |
| 0.0.32 | 2025-09-24 | [66464](https://github.com/airbytehq/airbyte/pull/66464) | Update dependencies |
| 0.0.31 | 2025-09-09 | [65657](https://github.com/airbytehq/airbyte/pull/65657) | Update dependencies |
| 0.0.30 | 2025-08-24 | [65441](https://github.com/airbytehq/airbyte/pull/65441) | Update dependencies |
| 0.0.29 | 2025-08-09 | [64807](https://github.com/airbytehq/airbyte/pull/64807) | Update dependencies |
| 0.0.28 | 2025-08-02 | [64311](https://github.com/airbytehq/airbyte/pull/64311) | Update dependencies |
| 0.0.27 | 2025-07-26 | [64083](https://github.com/airbytehq/airbyte/pull/64083) | Update dependencies |
| 0.0.26 | 2025-07-19 | [63633](https://github.com/airbytehq/airbyte/pull/63633) | Update dependencies |
| 0.0.25 | 2025-07-12 | [63199](https://github.com/airbytehq/airbyte/pull/63199) | Update dependencies |
| 0.0.24 | 2025-07-05 | [62672](https://github.com/airbytehq/airbyte/pull/62672) | Update dependencies |
| 0.0.23 | 2025-06-28 | [62251](https://github.com/airbytehq/airbyte/pull/62251) | Update dependencies |
| 0.0.22 | 2025-06-21 | [61768](https://github.com/airbytehq/airbyte/pull/61768) | Update dependencies |
| 0.0.21 | 2025-06-15 | [61261](https://github.com/airbytehq/airbyte/pull/61261) | Update dependencies |
| 0.0.20 | 2025-05-24 | [60768](https://github.com/airbytehq/airbyte/pull/60768) | Update dependencies |
| 0.0.19 | 2025-05-10 | [59923](https://github.com/airbytehq/airbyte/pull/59923) | Update dependencies |
| 0.0.18 | 2025-05-04 | [59543](https://github.com/airbytehq/airbyte/pull/59543) | Update dependencies |
| 0.0.17 | 2025-04-26 | [58031](https://github.com/airbytehq/airbyte/pull/58031) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57375](https://github.com/airbytehq/airbyte/pull/57375) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56816](https://github.com/airbytehq/airbyte/pull/56816) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56334](https://github.com/airbytehq/airbyte/pull/56334) | Update dependencies |
| 0.0.13 | 2025-03-09 | [55658](https://github.com/airbytehq/airbyte/pull/55658) | Update dependencies |
| 0.0.12 | 2025-03-01 | [55164](https://github.com/airbytehq/airbyte/pull/55164) | Update dependencies |
| 0.0.11 | 2025-02-23 | [54635](https://github.com/airbytehq/airbyte/pull/54635) | Update dependencies |
| 0.0.10 | 2025-02-16 | [54123](https://github.com/airbytehq/airbyte/pull/54123) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53598](https://github.com/airbytehq/airbyte/pull/53598) | Update dependencies |
| 0.0.8 | 2025-02-01 | [53121](https://github.com/airbytehq/airbyte/pull/53121) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52543](https://github.com/airbytehq/airbyte/pull/52543) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51932](https://github.com/airbytehq/airbyte/pull/51932) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51463](https://github.com/airbytehq/airbyte/pull/51463) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50833](https://github.com/airbytehq/airbyte/pull/50833) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50387](https://github.com/airbytehq/airbyte/pull/50387) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49446](https://github.com/airbytehq/airbyte/pull/49446) | Update dependencies |
| 0.0.1 | 2024-10-28 | [46863](https://github.com/airbytehq/airbyte/pull/46863) | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
