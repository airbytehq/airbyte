# Jotform
Jotform is a powerful online form builder that makes it easy to create robust forms and collect important data.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `end_date` | `string` | End date.  |  |
| `start_date` | `string` | Start date.  |  |
| `api_endpoint` | `object` | API Endpoint.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| submissions | id | DefaultPaginator | ✅ |  ✅  |
| reports | id | No pagination | ✅ |  ✅  |
| forms | id | DefaultPaginator | ✅ |  ✅  |
| questions | form_id.qid | No pagination | ✅ |  ❌  |
| form_properties | id | No pagination | ✅ |  ❌  |
| form_files | url | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-12 | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder|

</details>