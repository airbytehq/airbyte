# Survicate
New Source: Survicate
Website: https://survicate.com/
API docs: https://developers.survicate.com/data-export/setup/
API Authentication docs: https://developers.survicate.com/data-export/setup/#authentication

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| surveys | id | DefaultPaginator | ✅ |  ✅  |
| surveys_questions | id | DefaultPaginator | ✅ |  ❌  |
| surveys_responses | uuid | DefaultPaginator | ✅ |  ✅  |
| respondents_attributes |  | DefaultPaginator | ✅ |  ❌  |
| respondents_responses |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-05 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>