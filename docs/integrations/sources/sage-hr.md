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
| 0.0.14 | 2025-02-08 | [53496](https://github.com/airbytehq/airbyte/pull/53496) | Update dependencies |
| 0.0.13 | 2025-02-01 | [52966](https://github.com/airbytehq/airbyte/pull/52966) | Update dependencies |
| 0.0.12 | 2025-01-25 | [52505](https://github.com/airbytehq/airbyte/pull/52505) | Update dependencies |
| 0.0.11 | 2025-01-18 | [51899](https://github.com/airbytehq/airbyte/pull/51899) | Update dependencies |
| 0.0.10 | 2025-01-11 | [51323](https://github.com/airbytehq/airbyte/pull/51323) | Update dependencies |
| 0.0.9 | 2024-12-28 | [50687](https://github.com/airbytehq/airbyte/pull/50687) | Update dependencies |
| 0.0.8 | 2024-12-21 | [50300](https://github.com/airbytehq/airbyte/pull/50300) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49687](https://github.com/airbytehq/airbyte/pull/49687) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49353](https://github.com/airbytehq/airbyte/pull/49353) | Update dependencies |
| 0.0.5 | 2024-12-11 | [49089](https://github.com/airbytehq/airbyte/pull/49089) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-05 | [48353](https://github.com/airbytehq/airbyte/pull/48353) | Revert to source-declarative-manifest v5.17.0 |
| 0.0.3 | 2024-11-05 | [48328](https://github.com/airbytehq/airbyte/pull/48328) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47581](https://github.com/airbytehq/airbyte/pull/47581) | Update dependencies |
| 0.0.1 | 2024-10-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
