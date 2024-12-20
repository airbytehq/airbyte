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
| 0.0.6 | 2024-12-14 | [49615](https://github.com/airbytehq/airbyte/pull/49615) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49220](https://github.com/airbytehq/airbyte/pull/49220) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48319](https://github.com/airbytehq/airbyte/pull/48319) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-10-29 | [47926](https://github.com/airbytehq/airbyte/pull/47926) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47649](https://github.com/airbytehq/airbyte/pull/47649) | Update dependencies |
| 0.0.1 | 2024-09-03 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
