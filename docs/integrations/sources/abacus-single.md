# Abacus Single
Pulls data from Abacus POS With Incremetnal Refresh

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `admin_api_key` | `string` | HQ API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| invoices | invoiceNumber | DefaultPaginator | ✅ |  ✅  |
| products | productId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-12-04 | | Initial release by [@lukepetrovici-bi](https://github.com/lukepetrovici-bi) via Connector Builder |

</details>
