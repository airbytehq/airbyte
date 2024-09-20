# Dropbox Sign
Dropbox Sign is a simple, easy-to-use way to get documents signed securely online.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://app.hellosign.com/home/myAccount#api |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| signature_requests | signature_request_id | DefaultPaginator | ✅ |  ✅  |
| templates | template_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-20 | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder|

</details>