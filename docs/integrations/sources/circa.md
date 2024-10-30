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
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
