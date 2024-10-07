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
| documents-categories | id | No pagination | ✅ |  ❌  |
| documents | id | No pagination | ✅ |  ❌  |
| positions | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| terminated-employees | id | No pagination | ✅ |  ❌  |
| termination-reasons | id | No pagination | ✅ |  ❌  |
| policies | id | No pagination | ✅ |  ❌  |
| individual-allowances | id | No pagination | ✅ |  ❌  |
| document-categories | id | No pagination | ✅ |  ❌  |
| offboarding-categories | id | No pagination | ✅ |  ❌  |
| onboarding-categories | id | No pagination | ✅ |  ❌  |
| requests | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-07 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
