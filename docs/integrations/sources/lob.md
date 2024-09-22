# Lob
Website: https://dashboard.lob.com/
API docs: https://docs.lob.com/
Auth Docs: https://docs.lob.com/#tag/Authentication
Auth page: https://dashboard.lob.com/settings/api-keys

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use for authentication. You can find your account&#39;s API keys in your Dashboard Settings at https://dashboard.lob.com/settings/api-keys. |  |
| `start_date` | `string` | Start date.  |  |
| `limit` | `string` | Limit. Max records per page limit | 50 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| addresses | id | DefaultPaginator | ✅ |  ✅  |
| banks | id | DefaultPaginator | ✅ |  ✅  |
| postcards | id | DefaultPaginator | ✅ |  ✅  |
| templates | id | DefaultPaginator | ✅ |  ✅  |
| templates_versions | id | DefaultPaginator | ✅ |  ✅  |
| campaigns | id | DefaultPaginator | ✅ |  ✅  |
| uploads | id | DefaultPaginator | ✅ |  ✅  |
| qr_code_analytics | resource_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-22 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>