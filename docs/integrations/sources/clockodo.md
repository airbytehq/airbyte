# Clockodo
The Airbyte connector for Clockodo enables seamless data integration between Clockodo and your preferred data warehouse or destination. This connector allows you to efficiently extract time tracking, project management, and reporting data from Clockodo, providing accurate insights and facilitating informed business decisions.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it in the &#39;Personal data&#39; section of your Clockodo account. |  |
| `email_address` | `string` | Email Address. Your Clockodo account email address. Find it in your Clockodo account settings. |  |
| `external_application` | `string` | External Application Header. Identification of the calling application, including the email address of a technical contact person. Format: [name of application or company];[email address]. | Airbyte |
| `years` | `integer` | Year.  |  |
| `start_date` | `string` | Start Date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| projects | id | DefaultPaginator | ✅ |  ❌  |
| absences | id | No pagination | ✅ |  ❌  |
| customers | id | DefaultPaginator | ✅ |  ❌  |
| entries | id | DefaultPaginator | ✅ |  ✅  |
| holidays_carry | id | No pagination | ✅ |  ❌  |
| holidays_quota | id | No pagination | ✅ |  ❌  |
| lumpsum_services | id | No pagination | ✅ |  ❌  |
| non_business_days | id | No pagination | ✅ |  ❌  |
| overtime_carry | id | No pagination | ✅ |  ❌  |
| services | id | DefaultPaginator | ✅ |  ❌  |
| surcharges | id | No pagination | ✅ |  ❌  |
| target_hours | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| user_reports |  | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ❌  |
| customers_projects | user_id | No pagination | ✅ |  ❌  |
| access_services | user_id | No pagination | ✅ |  ❌  |
| work_times |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-02-01 | [52889](https://github.com/airbytehq/airbyte/pull/52889) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52370](https://github.com/airbytehq/airbyte/pull/52370) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51648](https://github.com/airbytehq/airbyte/pull/51648) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51135](https://github.com/airbytehq/airbyte/pull/51135) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50547](https://github.com/airbytehq/airbyte/pull/50547) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50067](https://github.com/airbytehq/airbyte/pull/50067) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49482](https://github.com/airbytehq/airbyte/pull/49482) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49163](https://github.com/airbytehq/airbyte/pull/49163) | Update dependencies |
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
