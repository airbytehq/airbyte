# Judge.me Reviews
Get Reviews from Judge.me Reviews: https://judge.me/
API: https://judge.me/api/docs#tag/Reviews/operation/reviews#index

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |
| `shop_domain` | `string` | Shop Domain. example.myshopify.com |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| reviews | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2025-07-12 | [63143](https://github.com/airbytehq/airbyte/pull/63143) | Update dependencies |
| 0.0.1 | 2025-06-18 | | Initial release by [@nmtruong93](https://github.com/nmtruong93) via Connector Builder |

</details>
