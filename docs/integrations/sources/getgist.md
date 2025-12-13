# GetGist
An Airbyte connector for [Gist](https://getgist.com/) would enable data syncing between Gist and various data platforms or databases. This connector could pull data from key objects like contacts, tags, segments, campaigns, forms, and subscription types, facilitating integration with other tools in a data pipeline. By automating data extraction from Gist, users can analyze customer interactions and engagement more efficiently in their preferred analytics or storage environment.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it in the Integration Settings on your Gist dashboard at https://app.getgist.com/projects/_/settings/api-key. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| collections | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | DefaultPaginator | ✅ |  ❌  |
| segments | id | DefaultPaginator | ✅ |  ❌  |
| forms | id | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| subscription_types | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| teammates | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70724](https://github.com/airbytehq/airbyte/pull/70724) | Update dependencies |
| 0.0.40 | 2025-11-25 | [69904](https://github.com/airbytehq/airbyte/pull/69904) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69384](https://github.com/airbytehq/airbyte/pull/69384) | Update dependencies |
| 0.0.38 | 2025-10-29 | [69006](https://github.com/airbytehq/airbyte/pull/69006) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68307](https://github.com/airbytehq/airbyte/pull/68307) | Update dependencies |
| 0.0.36 | 2025-10-14 | [68005](https://github.com/airbytehq/airbyte/pull/68005) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67260](https://github.com/airbytehq/airbyte/pull/67260) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66296](https://github.com/airbytehq/airbyte/pull/66296) | Update dependencies |
| 0.0.33 | 2025-09-09 | [66077](https://github.com/airbytehq/airbyte/pull/66077) | Update dependencies |
| 0.0.32 | 2025-08-23 | [65354](https://github.com/airbytehq/airbyte/pull/65354) | Update dependencies |
| 0.0.31 | 2025-08-09 | [64576](https://github.com/airbytehq/airbyte/pull/64576) | Update dependencies |
| 0.0.30 | 2025-08-02 | [64277](https://github.com/airbytehq/airbyte/pull/64277) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63467](https://github.com/airbytehq/airbyte/pull/63467) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63110](https://github.com/airbytehq/airbyte/pull/63110) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62783](https://github.com/airbytehq/airbyte/pull/62783) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62418](https://github.com/airbytehq/airbyte/pull/62418) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61971](https://github.com/airbytehq/airbyte/pull/61971) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61255](https://github.com/airbytehq/airbyte/pull/61255) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60385](https://github.com/airbytehq/airbyte/pull/60385) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59924](https://github.com/airbytehq/airbyte/pull/59924) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59400](https://github.com/airbytehq/airbyte/pull/59400) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58876](https://github.com/airbytehq/airbyte/pull/58876) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58360](https://github.com/airbytehq/airbyte/pull/58360) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57802](https://github.com/airbytehq/airbyte/pull/57802) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57242](https://github.com/airbytehq/airbyte/pull/57242) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56513](https://github.com/airbytehq/airbyte/pull/56513) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55979](https://github.com/airbytehq/airbyte/pull/55979) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55284](https://github.com/airbytehq/airbyte/pull/55284) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54457](https://github.com/airbytehq/airbyte/pull/54457) | Update dependencies |
| 0.0.12 | 2025-02-15 | [53725](https://github.com/airbytehq/airbyte/pull/53725) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53352](https://github.com/airbytehq/airbyte/pull/53352) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52830](https://github.com/airbytehq/airbyte/pull/52830) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52331](https://github.com/airbytehq/airbyte/pull/52331) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51653](https://github.com/airbytehq/airbyte/pull/51653) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51085](https://github.com/airbytehq/airbyte/pull/51085) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50512](https://github.com/airbytehq/airbyte/pull/50512) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50018](https://github.com/airbytehq/airbyte/pull/50018) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49532](https://github.com/airbytehq/airbyte/pull/49532) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49192](https://github.com/airbytehq/airbyte/pull/49192) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48908](https://github.com/airbytehq/airbyte/pull/48908) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
