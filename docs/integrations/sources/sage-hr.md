# Sage HR
The Sage HR Airbyte Connector enables seamless data integration, allowing you to extract employee and HR data from Sage HR into your preferred data warehouse or analytics tool. Simplify data syncing for effortless employee management and streamline HR workflows.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `subdomain` | `string` | subdomain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| employees | id | DefaultPaginator | ✅ |  ❌  |
| leave-management-policies | id | No pagination | ✅ |  ❌  |
| documents | id | DefaultPaginator | ✅ |  ❌  |
| positions | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| terminated-employees | id | DefaultPaginator | ✅ |  ❌  |
| termination-reasons | id | DefaultPaginator | ✅ |  ❌  |
| individual-allowances | id | DefaultPaginator | ✅ |  ❌  |
| document-categories | id | No pagination | ✅ |  ❌  |
| offboarding-categories | id | DefaultPaginator | ✅ |  ❌  |
| onboarding-categories | id | DefaultPaginator | ✅ |  ❌  |
| leave-requests | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
