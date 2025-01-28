# Repairshopr
Repairshopr is a CRM and an integrated marketing platform.
With this connector we can extract data from various streams such as customers , invoices and payments.
[API Documentation](https://api-docs.repairshopr.com/)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `subdomain` | `string` | Sub Domain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| appointment types | id | No pagination | ✅ |  ❌  |
| appointments | id | DefaultPaginator | ✅ |  ❌  |
| customer assets | id | DefaultPaginator | ✅ |  ❌  |
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
| 0.0.9 | 2025-01-25 | [52531](https://github.com/airbytehq/airbyte/pull/52531) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51909](https://github.com/airbytehq/airbyte/pull/51909) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51367](https://github.com/airbytehq/airbyte/pull/51367) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50682](https://github.com/airbytehq/airbyte/pull/50682) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50255](https://github.com/airbytehq/airbyte/pull/50255) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49690](https://github.com/airbytehq/airbyte/pull/49690) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49366](https://github.com/airbytehq/airbyte/pull/49366) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49092](https://github.com/airbytehq/airbyte/pull/49092) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
