# Client Success
Connector for the working Client Success API endpoints

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `start_date` | `string` | Start date.  |  |
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Clients | id | DefaultPaginator | ✅ |  ✅  |
| Contacts | id | DefaultPaginator | ✅ |  ✅  |
| Contracts | id | DefaultPaginator | ✅ |  ✅  |
| Products | id | DefaultPaginator | ✅ |  ✅  |
| Custom Fields | fieldId | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-25 | Initial release by [@MindNumbing](https://github.com/MindNumbing) via Connector Builder|

</details>