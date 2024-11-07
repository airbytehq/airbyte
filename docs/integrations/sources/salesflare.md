# Salesflare
Salesflare is a CRM tool for small and medium businesses.
Using this connector we can extract data from various streams such as opportunities , workflows and pipelines.
Docs : https://api.salesflare.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Enter you api key like this : Bearer YOUR_API_KEY |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| opportunities | id | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| persons | id | No pagination | ✅ |  ❌  |
| email data sources | id | No pagination | ✅ |  ❌  |
| custom field types | id | No pagination | ✅ |  ❌  |
| pipelines | id | No pagination | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-07 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
