# Google Tasks V2
Website: https://tasksboard.com/app
API Docs: https://developers.google.com/tasks/reference/rest
Auth Docs: https://support.google.com/googleapi/answer/6158849?hl=en&amp;ref_topic=7013279

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `records_limit` | `string` | Records Limit. The maximum number of records to be returned per request | 50 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ✅  |
| lists_tasks | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-25 | Initial release by [@erohmensing](https://github.com/erohmensing) via Connector Builder|

</details>