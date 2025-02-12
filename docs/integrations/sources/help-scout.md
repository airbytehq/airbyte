# Help Scout
Connector for Help Scout Inbox API 2.0: https://developer.helpscout.com/mailbox-api/
Auth Overview: https://developer.helpscout.com/mailbox-api/overview/authentication/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Application ID.  |  |
| `client_secret` | `string` | Application Secret.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| conversations | id | DefaultPaginator | ✅ |  ✅  |
| conversation_threads | id | DefaultPaginator | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| inboxes | id | DefaultPaginator | ✅ |  ❌  |
| inbox_custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| inbox_folders | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| team_members | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request                                         | Subject        |
|------------------|-------------------|------------------------------------------------------|----------------|
| 0.0.3 | 2025-02-08 | [53281](https://github.com/airbytehq/airbyte/pull/53281) | Update dependencies |
| 0.0.2 | 2025-02-01 | [52784](https://github.com/airbytehq/airbyte/pull/52784) | Update dependencies |
| 0.0.1 | 2025-01-28 | [52614](https://github.com/airbytehq/airbyte/pull/52614) | Initial release by [@pabloescoder](https://github.com/pabloescoder) via Connector Builder |

</details>
