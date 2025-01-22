# Invoiceninja
Invoice Ninja is an invoicing, billing, and payment management software.
With this connector we can extract data from various streams such asproducts , invoice , payments and quotes.
Docs : https://api-docs.invoicing.co/#overview--introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| clients | id | DefaultPaginator | ✅ |  ❌  |
| products | id | DefaultPaginator | ✅ |  ❌  |
| invoices | id | DefaultPaginator | ✅ |  ❌  |
| recurring invoices | id | DefaultPaginator | ✅ |  ❌  |
| payments | id | DefaultPaginator | ✅ |  ❌  |
| quotes | id | DefaultPaginator | ✅ |  ❌  |
| credits | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| vendors | id | DefaultPaginator | ✅ |  ❌  |
| purchase_orders | id | DefaultPaginator | ✅ |  ❌  |
| expenses | id | DefaultPaginator | ✅ |  ❌  |
| recurring expenses | id | DefaultPaginator | ✅ |  ❌  |
| bank transactions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-01-18 | [51780](https://github.com/airbytehq/airbyte/pull/51780) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51179](https://github.com/airbytehq/airbyte/pull/51179) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50664](https://github.com/airbytehq/airbyte/pull/50664) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50134](https://github.com/airbytehq/airbyte/pull/50134) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49605](https://github.com/airbytehq/airbyte/pull/49605) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49234](https://github.com/airbytehq/airbyte/pull/49234) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48917](https://github.com/airbytehq/airbyte/pull/48917) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-07 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
