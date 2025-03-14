# Jotform
Jotform is a powerful online form builder that makes it easy to create robust forms and collect important data.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `end_date` | `string` | End date to filter submissions, reports, forms, form_files streams incrementally.  |  |
| `start_date` | `string` | Start date to filter submissions, reports, forms, form_files streams incrementally.  |  |
| `api_endpoint` | `object` | API Endpoint.  |  |

To get started, you need a valid API key.
1. Go to [My Account](https://www.jotform.com/myaccount/api)
2. Navigate to API Section
3. Create a new API Key

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| submissions | id | DefaultPaginator | ✅ |  ✅  |
| reports | id | No pagination | ✅ |  ✅  |
| forms | id | DefaultPaginator | ✅ |  ✅  |
| questions | form_id.qid | No pagination | ✅ |  ❌  |
| form_properties | id | No pagination | ✅ |  ❌  |
| form_files | url | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.12 | 2025-03-08 | [55467](https://github.com/airbytehq/airbyte/pull/55467) | Update dependencies |
| 0.0.11 | 2025-03-01 | [54802](https://github.com/airbytehq/airbyte/pull/54802) | Update dependencies |
| 0.0.10 | 2025-02-22 | [54338](https://github.com/airbytehq/airbyte/pull/54338) | Update dependencies |
| 0.0.9 | 2025-02-15 | [51804](https://github.com/airbytehq/airbyte/pull/51804) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51168](https://github.com/airbytehq/airbyte/pull/51168) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50100](https://github.com/airbytehq/airbyte/pull/50100) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49608](https://github.com/airbytehq/airbyte/pull/49608) | Update dependencies |
| 0.0.5 | 2024-12-12 | [48965](https://github.com/airbytehq/airbyte/pull/48965) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48179](https://github.com/airbytehq/airbyte/pull/48179) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47930](https://github.com/airbytehq/airbyte/pull/47930) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47603](https://github.com/airbytehq/airbyte/pull/47603) | Update dependencies |
| 0.0.1 | 2024-09-12 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
