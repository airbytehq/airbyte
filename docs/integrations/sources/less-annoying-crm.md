# Less Annoying CRM
Less Annoying CRM connector  enables seamless data integration, allowing users to easily sync customer relationship management data into their data warehouses or analytics tools. This connector facilitates efficient tracking of customer information, interactions, and leads, helping businesses centralize CRM data for enhanced analysis and insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Manage and create your API keys on the Programmer API settings page at https://account.lessannoyingcrm.com/app/Settings/Api. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users |  | DefaultPaginator | ✅ |  ❌  |
| contacts | ContactId | DefaultPaginator | ✅ |  ❌  |
| tasks |  | DefaultPaginator | ✅ |  ✅  |
| pipeline_items | PipelineItemId | DefaultPaginator | ✅ |  ❌  |
| notes | NoteId | DefaultPaginator | ✅ |  ❌  |
| teams | TeamId | No pagination | ✅ |  ❌  |
| events | EventId | DefaultPaginator | ✅ |  ✅  |
| contact_events |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70756](https://github.com/airbytehq/airbyte/pull/70756) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70054](https://github.com/airbytehq/airbyte/pull/70054) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69445](https://github.com/airbytehq/airbyte/pull/69445) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68979](https://github.com/airbytehq/airbyte/pull/68979) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68316](https://github.com/airbytehq/airbyte/pull/68316) | Update dependencies |
| 0.0.36 | 2025-10-14 | [68025](https://github.com/airbytehq/airbyte/pull/68025) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67522](https://github.com/airbytehq/airbyte/pull/67522) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66809](https://github.com/airbytehq/airbyte/pull/66809) | Update dependencies |
| 0.0.33 | 2025-09-24 | [66645](https://github.com/airbytehq/airbyte/pull/66645) | Update dependencies |
| 0.0.32 | 2025-09-09 | [66086](https://github.com/airbytehq/airbyte/pull/66086) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65388](https://github.com/airbytehq/airbyte/pull/65388) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64635](https://github.com/airbytehq/airbyte/pull/64635) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64223](https://github.com/airbytehq/airbyte/pull/64223) | Update dependencies |
| 0.0.28 | 2025-07-26 | [63853](https://github.com/airbytehq/airbyte/pull/63853) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63511](https://github.com/airbytehq/airbyte/pull/63511) | Update dependencies |
| 0.0.26 | 2025-07-12 | [63127](https://github.com/airbytehq/airbyte/pull/63127) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62546](https://github.com/airbytehq/airbyte/pull/62546) | Update dependencies |
| 0.0.24 | 2025-06-28 | [62183](https://github.com/airbytehq/airbyte/pull/62183) | Update dependencies |
| 0.0.23 | 2025-06-21 | [61835](https://github.com/airbytehq/airbyte/pull/61835) | Update dependencies |
| 0.0.22 | 2025-06-14 | [60590](https://github.com/airbytehq/airbyte/pull/60590) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59792](https://github.com/airbytehq/airbyte/pull/59792) | Update dependencies |
| 0.0.20 | 2025-05-03 | [59279](https://github.com/airbytehq/airbyte/pull/59279) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58753](https://github.com/airbytehq/airbyte/pull/58753) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58179](https://github.com/airbytehq/airbyte/pull/58179) | Update dependencies |
| 0.0.17 | 2025-04-12 | [57748](https://github.com/airbytehq/airbyte/pull/57748) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57047](https://github.com/airbytehq/airbyte/pull/57047) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56639](https://github.com/airbytehq/airbyte/pull/56639) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56036](https://github.com/airbytehq/airbyte/pull/56036) | Update dependencies |
| 0.0.13 | 2025-03-08 | [55507](https://github.com/airbytehq/airbyte/pull/55507) | Update dependencies |
| 0.0.12 | 2025-03-01 | [54753](https://github.com/airbytehq/airbyte/pull/54753) | Update dependencies |
| 0.0.11 | 2025-02-22 | [54331](https://github.com/airbytehq/airbyte/pull/54331) | Update dependencies |
| 0.0.10 | 2025-02-15 | [53843](https://github.com/airbytehq/airbyte/pull/53843) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53269](https://github.com/airbytehq/airbyte/pull/53269) | Update dependencies |
| 0.0.8 | 2025-02-01 | [52759](https://github.com/airbytehq/airbyte/pull/52759) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52231](https://github.com/airbytehq/airbyte/pull/52231) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51826](https://github.com/airbytehq/airbyte/pull/51826) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51143](https://github.com/airbytehq/airbyte/pull/51143) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50665](https://github.com/airbytehq/airbyte/pull/50665) | Update dependencies |
| 0.0.3 | 2024-12-21 | [49606](https://github.com/airbytehq/airbyte/pull/49606) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49227](https://github.com/airbytehq/airbyte/pull/49227) | Update dependencies |
| 0.0.1 | 2024-10-31 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
