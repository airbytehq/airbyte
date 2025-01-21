# Nylas
The Nylas platform provides an integration layer that makes it easy to connect and sync email, calendar, and contact data from any email service provider.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `api_server` | `string` | API Server.  |  |
| `start_date` | `string` | Start date.  |  |
| `end_date` | `string` | End date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| calendars | id | DefaultPaginator | ✅ |  ❌  |
| connectors |  | No pagination | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| credentials |  | No pagination | ✅ |  ❌  |
| drafts | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| folders | id | DefaultPaginator | ✅ |  ❌  |
| grants | id | DefaultPaginator | ✅ |  ❌  |
| messages | id | DefaultPaginator | ✅ |  ✅  |
| scheduled_messages | schedule_id | No pagination | ✅ |  ❌  |
| threads | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.1 | 2024-09-03 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>