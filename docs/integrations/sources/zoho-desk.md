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
| 0.0.7 | 2025-01-25 | [52543](https://github.com/airbytehq/airbyte/pull/52543) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51932](https://github.com/airbytehq/airbyte/pull/51932) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51463](https://github.com/airbytehq/airbyte/pull/51463) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50833](https://github.com/airbytehq/airbyte/pull/50833) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50387](https://github.com/airbytehq/airbyte/pull/50387) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49446](https://github.com/airbytehq/airbyte/pull/49446) | Update dependencies |
| 0.0.1 | 2024-10-28 | [46863](https://github.com/airbytehq/airbyte/pull/46863) | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
