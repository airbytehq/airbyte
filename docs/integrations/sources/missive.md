# Missive
Website: https://missiveapp.com/
API Docs: https://missiveapp.com/help/api-documentation/rest-endpoints
Auth Docs: https://missiveapp.com/help/api-documentation/getting-started

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |
| `start_date` | `string` | Start date.  |  |
| `kind` | `string` | Kind. Kind parameter for `contact_groups` stream | group |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contact_books | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| contact_groups | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| shared_labels | id | DefaultPaginator | ✅ |  ❌  |
| organizations | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-22 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>