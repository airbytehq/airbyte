# Zoho Expense
Zoho Expense is a Travel and expense management for growing businesses.
With this connector we can extract data from various streams such as trips , expense details , expense reports and contacts streams

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `region` | `string` | Region. The region code for the Zoho Books API, such as &#39;com&#39;, &#39;eu&#39;, &#39;in&#39;, etc. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| trips | trip_id | DefaultPaginator | ✅ |  ❌  |
| expense details | expense_id | DefaultPaginator | ✅ |  ❌  |
| expense reports | report_id | DefaultPaginator | ✅ |  ❌  |
| users | user_id | DefaultPaginator | ✅ |  ❌  |
| Taxes | tax_id | DefaultPaginator | ✅ |  ❌  |
| contacts | contact_id | DefaultPaginator | ✅ |  ❌  |
| projects | project_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-27 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
