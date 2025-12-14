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
| 0.0.42 | 2025-12-09 | [70618](https://github.com/airbytehq/airbyte/pull/70618) | Update dependencies |
| 0.0.41 | 2025-11-25 | [69931](https://github.com/airbytehq/airbyte/pull/69931) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69592](https://github.com/airbytehq/airbyte/pull/69592) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68874](https://github.com/airbytehq/airbyte/pull/68874) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68520](https://github.com/airbytehq/airbyte/pull/68520) | Update dependencies |
| 0.0.37 | 2025-10-14 | [68076](https://github.com/airbytehq/airbyte/pull/68076) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67185](https://github.com/airbytehq/airbyte/pull/67185) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66250](https://github.com/airbytehq/airbyte/pull/66250) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65790](https://github.com/airbytehq/airbyte/pull/65790) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65247](https://github.com/airbytehq/airbyte/pull/65247) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64737](https://github.com/airbytehq/airbyte/pull/64737) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64351](https://github.com/airbytehq/airbyte/pull/64351) | Update dependencies |
| 0.0.30 | 2025-07-26 | [64037](https://github.com/airbytehq/airbyte/pull/64037) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63566](https://github.com/airbytehq/airbyte/pull/63566) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63016](https://github.com/airbytehq/airbyte/pull/63016) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62756](https://github.com/airbytehq/airbyte/pull/62756) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62361](https://github.com/airbytehq/airbyte/pull/62361) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61956](https://github.com/airbytehq/airbyte/pull/61956) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61253](https://github.com/airbytehq/airbyte/pull/61253) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60379](https://github.com/airbytehq/airbyte/pull/60379) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60036](https://github.com/airbytehq/airbyte/pull/60036) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59438](https://github.com/airbytehq/airbyte/pull/59438) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58869](https://github.com/airbytehq/airbyte/pull/58869) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58362](https://github.com/airbytehq/airbyte/pull/58362) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57818](https://github.com/airbytehq/airbyte/pull/57818) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57262](https://github.com/airbytehq/airbyte/pull/57262) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56544](https://github.com/airbytehq/airbyte/pull/56544) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55957](https://github.com/airbytehq/airbyte/pull/55957) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55279](https://github.com/airbytehq/airbyte/pull/55279) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54979](https://github.com/airbytehq/airbyte/pull/54979) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54389](https://github.com/airbytehq/airbyte/pull/54389) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53732](https://github.com/airbytehq/airbyte/pull/53732) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53430](https://github.com/airbytehq/airbyte/pull/53430) | Update dependencies |
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
