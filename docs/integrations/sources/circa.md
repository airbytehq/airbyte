# Simple Circa
Airbyte connector for [SimpleCirca](https://www.simplecirca.com/) would enable seamless data extraction from Simple Circa's platform, facilitating automated data integration into your data warehouse or analytics systems. This connector would pull key metrics, user engagement data, and content performance insights, offering streamlined reporting and analysis workflows. Ideal for organizations looking to consolidate Circa’s data with other sources for comprehensive business intelligence.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://app.circa.co/settings/integrations/api |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ✅  |
| contacts | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| companies |  | DefaultPaginator | ✅ |  ✅  |
| company_contacts | id | DefaultPaginator | ✅ |  ❌  |
| event_fields | id | No pagination | ✅ |  ❌  |
| contact_fields | id | No pagination | ✅ |  ❌  |
| company_fields | id | No pagination | ✅ |  ❌  |
| event_contacts | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-02-01 | [52920](https://github.com/airbytehq/airbyte/pull/52920) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52190](https://github.com/airbytehq/airbyte/pull/52190) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51754](https://github.com/airbytehq/airbyte/pull/51754) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51281](https://github.com/airbytehq/airbyte/pull/51281) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50487](https://github.com/airbytehq/airbyte/pull/50487) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50197](https://github.com/airbytehq/airbyte/pull/50197) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49545](https://github.com/airbytehq/airbyte/pull/49545) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49313](https://github.com/airbytehq/airbyte/pull/49313) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49034](https://github.com/airbytehq/airbyte/pull/49034) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-11-04 | [48268](https://github.com/airbytehq/airbyte/pull/48268) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
