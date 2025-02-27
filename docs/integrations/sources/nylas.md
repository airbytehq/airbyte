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
| 0.0.15 | 2025-02-23 | [54622](https://github.com/airbytehq/airbyte/pull/54622) | Update dependencies |
| 0.0.14 | 2025-02-15 | [54012](https://github.com/airbytehq/airbyte/pull/54012) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53499](https://github.com/airbytehq/airbyte/pull/53499) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52775](https://github.com/airbytehq/airbyte/pull/52775) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52265](https://github.com/airbytehq/airbyte/pull/52265) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51845](https://github.com/airbytehq/airbyte/pull/51845) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51167](https://github.com/airbytehq/airbyte/pull/51167) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50641](https://github.com/airbytehq/airbyte/pull/50641) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50112](https://github.com/airbytehq/airbyte/pull/50112) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49615](https://github.com/airbytehq/airbyte/pull/49615) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49220](https://github.com/airbytehq/airbyte/pull/49220) | Update dependencies |
| 0.0.4 | 2024-12-11 | [48319](https://github.com/airbytehq/airbyte/pull/48319) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-10-29 | [47926](https://github.com/airbytehq/airbyte/pull/47926) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47649](https://github.com/airbytehq/airbyte/pull/47649) | Update dependencies |
| 0.0.1 | 2024-09-03 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
