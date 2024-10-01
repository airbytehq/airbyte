# Easypost
Website: https://www.easypost.com/
API Docs: https://docs.easypost.com/docs/addresses
Auth Docs: https://docs.easypost.com/docs/authentication

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | API Key. The API Key from your easypost settings |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| batches | id | DefaultPaginator | ✅ |  ✅  |
| addresses | id | DefaultPaginator | ✅ |  ❌  |
| trackers | id | DefaultPaginator | ✅ |  ✅  |
| metadata_carriers | name | No pagination | ✅ |  ❌  |
| end_shippers | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ✅  |
| users_children | id | DefaultPaginator | ✅ |  ✅  |
| carrier_accounts | id | DefaultPaginator | ✅ |  ✅  |
| api_keys | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-01 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
