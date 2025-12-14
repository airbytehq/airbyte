# JobNimbus
The JobNimbus Airbyte connector enables seamless integration between JobNimbus, a popular CRM and project management tool, and your data pipeline. This connector allows you to automatically sync data from JobNimbus, including contacts records, task information, and more, into your preferred destination. It simplifies data extraction and helps you streamline workflows, enabling efficient analysis and reporting for enhanced business insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it by logging into your JobNimbus account, navigating to settings, and creating a new API key under the API section. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| jobs | jnid | DefaultPaginator | ✅ |  ❌  |
| contacts | jnid | DefaultPaginator | ✅ |  ❌  |
| tasks | jnid | DefaultPaginator | ✅ |  ❌  |
| activities | jnid | DefaultPaginator | ✅ |  ❌  |
| files | jnid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70474](https://github.com/airbytehq/airbyte/pull/70474) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70165](https://github.com/airbytehq/airbyte/pull/70165) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69560](https://github.com/airbytehq/airbyte/pull/69560) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68822](https://github.com/airbytehq/airbyte/pull/68822) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68539](https://github.com/airbytehq/airbyte/pull/68539) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67953](https://github.com/airbytehq/airbyte/pull/67953) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67358](https://github.com/airbytehq/airbyte/pull/67358) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66796](https://github.com/airbytehq/airbyte/pull/66796) | Update dependencies |
| 0.0.33 | 2025-09-09 | [66069](https://github.com/airbytehq/airbyte/pull/66069) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65357](https://github.com/airbytehq/airbyte/pull/65357) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64582](https://github.com/airbytehq/airbyte/pull/64582) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64274](https://github.com/airbytehq/airbyte/pull/64274) | Update dependencies |
| 0.0.29 | 2025-07-26 | [63906](https://github.com/airbytehq/airbyte/pull/63906) | Update dependencies |
| 0.0.28 | 2025-07-19 | [63532](https://github.com/airbytehq/airbyte/pull/63532) | Update dependencies |
| 0.0.27 | 2025-07-12 | [63102](https://github.com/airbytehq/airbyte/pull/63102) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62663](https://github.com/airbytehq/airbyte/pull/62663) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62157](https://github.com/airbytehq/airbyte/pull/62157) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61859](https://github.com/airbytehq/airbyte/pull/61859) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61140](https://github.com/airbytehq/airbyte/pull/61140) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60688](https://github.com/airbytehq/airbyte/pull/60688) | Update dependencies |
| 0.0.21 | 2025-05-10 | [59827](https://github.com/airbytehq/airbyte/pull/59827) | Update dependencies |
| 0.0.20 | 2025-05-03 | [58164](https://github.com/airbytehq/airbyte/pull/58164) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57718](https://github.com/airbytehq/airbyte/pull/57718) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57067](https://github.com/airbytehq/airbyte/pull/57067) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56715](https://github.com/airbytehq/airbyte/pull/56715) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56010](https://github.com/airbytehq/airbyte/pull/56010) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55453](https://github.com/airbytehq/airbyte/pull/55453) | Update dependencies |
| 0.0.14 | 2025-03-01 | [54819](https://github.com/airbytehq/airbyte/pull/54819) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54302](https://github.com/airbytehq/airbyte/pull/54302) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53819](https://github.com/airbytehq/airbyte/pull/53819) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53261](https://github.com/airbytehq/airbyte/pull/53261) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52769](https://github.com/airbytehq/airbyte/pull/52769) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52235](https://github.com/airbytehq/airbyte/pull/52235) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51817](https://github.com/airbytehq/airbyte/pull/51817) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51192](https://github.com/airbytehq/airbyte/pull/51192) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50661](https://github.com/airbytehq/airbyte/pull/50661) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50145](https://github.com/airbytehq/airbyte/pull/50145) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49610](https://github.com/airbytehq/airbyte/pull/49610) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49239](https://github.com/airbytehq/airbyte/pull/49239) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48919](https://github.com/airbytehq/airbyte/pull/48919) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-29 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
