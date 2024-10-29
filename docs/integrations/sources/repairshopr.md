# Repairshopr
Repairshopr is a CRM and an integrated marketing platform.
With this connector we can extract data from various streams such as customers , invoices and payments.
Docs : https://api-docs.repairshopr.com/#/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| appointment types |  | DefaultPaginator | ✅ |  ❌  |
| appointments | id | No pagination | ✅ |  ❌  |
| customer assets | id | No pagination | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| contracts | id | DefaultPaginator | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| estimates | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| items | id | DefaultPaginator | ✅ |  ❌  |
| line items | id | DefaultPaginator | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| payments | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
