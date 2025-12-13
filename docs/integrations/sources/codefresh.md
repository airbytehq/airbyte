# Codefresh
This connector integrates [Codefresh](https://codefresh.io) with Airbyte, enabling seamless data synchronization for analytics and pipeline monitoring. 
It provides streams like agents, builds, audit, analytics etc.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `account_id` | `string` | Account Id.  |  |
| `report_granularity` | `string` | Report Granularity.  |  |
| `report_date_range` | `array` | Report Date Range.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | _id | No pagination | ✅ |  ❌  |
| account_settings | _id | No pagination | ✅ |  ❌  |
| agents | id | No pagination | ✅ |  ❌  |
| builds | id | DefaultPaginator | ✅ |  ✅  |
| audit | id | DefaultPaginator | ✅ |  ✅  |
| analytics_metadata | reportName | No pagination | ✅ |  ❌  |
| analytics_reports |  | No pagination | ✅ |  ❌  |
| execution_contexts | _id | No pagination | ✅ |  ❌  |
| contexts | metadata | No pagination | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | metadata | DefaultPaginator | ✅ |  ❌  |
| step_types | metadata | DefaultPaginator | ✅ |  ❌  |
| helm_repos |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70650](https://github.com/airbytehq/airbyte/pull/70650) | Update dependencies |
| 0.0.40 | 2025-11-25 | [69925](https://github.com/airbytehq/airbyte/pull/69925) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69619](https://github.com/airbytehq/airbyte/pull/69619) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68921](https://github.com/airbytehq/airbyte/pull/68921) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68488](https://github.com/airbytehq/airbyte/pull/68488) | Update dependencies |
| 0.0.36 | 2025-10-14 | [68074](https://github.com/airbytehq/airbyte/pull/68074) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67189](https://github.com/airbytehq/airbyte/pull/67189) | Update dependencies |
| 0.0.34 | 2025-09-30 | [65772](https://github.com/airbytehq/airbyte/pull/65772) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65284](https://github.com/airbytehq/airbyte/pull/65284) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64739](https://github.com/airbytehq/airbyte/pull/64739) | Update dependencies |
| 0.0.31 | 2025-07-26 | [64032](https://github.com/airbytehq/airbyte/pull/64032) | Update dependencies |
| 0.0.30 | 2025-07-19 | [63539](https://github.com/airbytehq/airbyte/pull/63539) | Update dependencies |
| 0.0.29 | 2025-07-12 | [62978](https://github.com/airbytehq/airbyte/pull/62978) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62815](https://github.com/airbytehq/airbyte/pull/62815) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62307](https://github.com/airbytehq/airbyte/pull/62307) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61964](https://github.com/airbytehq/airbyte/pull/61964) | Update dependencies |
| 0.0.25 | 2025-06-14 | [61240](https://github.com/airbytehq/airbyte/pull/61240) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60360](https://github.com/airbytehq/airbyte/pull/60360) | Update dependencies |
| 0.0.23 | 2025-05-10 | [59939](https://github.com/airbytehq/airbyte/pull/59939) | Update dependencies |
| 0.0.22 | 2025-05-03 | [59417](https://github.com/airbytehq/airbyte/pull/59417) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58868](https://github.com/airbytehq/airbyte/pull/58868) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58346](https://github.com/airbytehq/airbyte/pull/58346) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57778](https://github.com/airbytehq/airbyte/pull/57778) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57275](https://github.com/airbytehq/airbyte/pull/57275) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56492](https://github.com/airbytehq/airbyte/pull/56492) | Update dependencies |
| 0.0.16 | 2025-03-22 | [55338](https://github.com/airbytehq/airbyte/pull/55338) | Update dependencies |
| 0.0.15 | 2025-03-01 | [54977](https://github.com/airbytehq/airbyte/pull/54977) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54433](https://github.com/airbytehq/airbyte/pull/54433) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53764](https://github.com/airbytehq/airbyte/pull/53764) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53361](https://github.com/airbytehq/airbyte/pull/53361) | Update dependencies |
| 0.0.11 | 2025-02-01 | [52802](https://github.com/airbytehq/airbyte/pull/52802) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52378](https://github.com/airbytehq/airbyte/pull/52378) | Update dependencies |
| 0.0.9 | 2025-01-18 | [51668](https://github.com/airbytehq/airbyte/pull/51668) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51088](https://github.com/airbytehq/airbyte/pull/51088) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50559](https://github.com/airbytehq/airbyte/pull/50559) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50051](https://github.com/airbytehq/airbyte/pull/50051) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49486](https://github.com/airbytehq/airbyte/pull/49486) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49182](https://github.com/airbytehq/airbyte/pull/49182) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48183](https://github.com/airbytehq/airbyte/pull/48183) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47574](https://github.com/airbytehq/airbyte/pull/47574) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
