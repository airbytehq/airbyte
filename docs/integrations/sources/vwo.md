# VWO
Website: https://app.vwo.com/
API Docs: https://developers.vwo.com/reference/introduction-1
Auth doc: https://developers.vwo.com/reference/authentication-for-personal-use-of-api-1
Auth page: https://app.vwo.com/#/developers/tokens

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ✅  |
| accounts_feeds | id | DefaultPaginator | ✅ |  ✅  |
| users | id | DefaultPaginator | ✅ |  ✅  |
| smartcode | uid | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ✅  |
| custom_widgets | id | DefaultPaginator | ✅ |  ✅  |
| thresholds | uid | DefaultPaginator | ✅ |  ❌  |
| integrations | uid | DefaultPaginator | ✅ |  ❌  |
| labels | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-23 | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder|

</details>