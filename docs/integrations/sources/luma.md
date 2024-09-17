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

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-08-28 | Initial release by [@natikgadzhi](https://github.com/natikgadzhi) via Connector Builder|

</details>