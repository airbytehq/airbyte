# Zoho Desk
This directory contains the manifest-only connector for source-zoho-desk

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| organization | id | No pagination | ✅ |  ❌  |
| organizations | id | No pagination | ✅ |  ❌  |
| accessible_organizations |  | DefaultPaginator | ✅ |  ❌  |
| agent |  | DefaultPaginator | ✅ |  ❌  |
| agents | id | DefaultPaginator | ✅ |  ❌  |
| agent_details_by_id | id | DefaultPaginator | ✅ |  ❌  |
| profiles | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| team_members | id | DefaultPaginator | ✅ |  ❌  |
| departments |  | DefaultPaginator | ✅ |  ❌  |
| channels | code | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |
| all_threads | id | DefaultPaginator | ✅ |  ❌  |
| get_latest_thread | id | DefaultPaginator | ✅ |  ❌  |
| list_contacts | id | DefaultPaginator | ✅ |  ❌  |
| webhooks |  | DefaultPaginator | ✅ |  ❌  |
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| contracts | id | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| articles | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| modules | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| ticket_activities | id | DefaultPaginator | ✅ |  ❌  |
| product_attachments |  | DefaultPaginator | ✅ |  ❌  |
| product | id | DefaultPaginator | ✅ |  ❌  |
| task_attachments | id | DefaultPaginator | ✅ |  ❌  |
| calls | id | DefaultPaginator | ✅ |  ❌  |
| call | id | DefaultPaginator | ✅ |  ❌  |
| call_comments | id | DefaultPaginator | ✅ |  ❌  |
| dashboard |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-14 | | Initial release by [@itsxdamdam](https://github.com/itsxdamdam) via Connector Builder |

</details>
