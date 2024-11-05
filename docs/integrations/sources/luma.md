# lu.ma


## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Get your API key on lu.ma Calendars dashboard → Settings. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | api_id | DefaultPaginator | ✅ |  ❌  |
| event-guests | api_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.4 | 2024-11-05 | [48327](https://github.com/airbytehq/airbyte/pull/48327) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47746](https://github.com/airbytehq/airbyte/pull/47746) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47669](https://github.com/airbytehq/airbyte/pull/47669) | Update dependencies |
| 0.0.1 | 2024-08-28 | | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder |

</details>
