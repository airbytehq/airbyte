# SparkPost
The SparkPost connector for Airbyte enables seamless integration with SparkPost’s email delivery service, allowing users to automatically sync email performance data, including delivery, open, and click metrics, into their data warehouses.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date.  |  |
| `api_prefix` | `string` | API Endpoint Prefix (`api` or `api.eu`)  | api |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| message_events | event_id | DefaultPaginator | ✅ |  ❌  |
| sending_domains | domain | No pagination | ✅ |  ❌  |
| ab_test | id | No pagination | ✅ |  ❌  |
| templates | id | No pagination | ✅ |  ❌  |
| recipients | id | No pagination | ✅ |  ❌  |
| subaccounts | id | DefaultPaginator | ✅ |  ❌  |
| snippets | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.40 | 2025-12-09 | [70605](https://github.com/airbytehq/airbyte/pull/70605) | Update dependencies |
| 0.0.39 | 2025-11-25 | [70024](https://github.com/airbytehq/airbyte/pull/70024) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69591](https://github.com/airbytehq/airbyte/pull/69591) | Update dependencies |
| 0.0.37 | 2025-10-29 | [68783](https://github.com/airbytehq/airbyte/pull/68783) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68261](https://github.com/airbytehq/airbyte/pull/68261) | Update dependencies |
| 0.0.35 | 2025-10-14 | [67755](https://github.com/airbytehq/airbyte/pull/67755) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67438](https://github.com/airbytehq/airbyte/pull/67438) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66903](https://github.com/airbytehq/airbyte/pull/66903) | Update dependencies |
| 0.0.32 | 2025-09-24 | [66271](https://github.com/airbytehq/airbyte/pull/66271) | Update dependencies |
| 0.0.31 | 2025-09-09 | [65714](https://github.com/airbytehq/airbyte/pull/65714) | Update dependencies |
| 0.0.30 | 2025-08-24 | [65459](https://github.com/airbytehq/airbyte/pull/65459) | Update dependencies |
| 0.0.29 | 2025-08-09 | [64830](https://github.com/airbytehq/airbyte/pull/64830) | Update dependencies |
| 0.0.28 | 2025-08-02 | [64415](https://github.com/airbytehq/airbyte/pull/64415) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63648](https://github.com/airbytehq/airbyte/pull/63648) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62748](https://github.com/airbytehq/airbyte/pull/62748) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62223](https://github.com/airbytehq/airbyte/pull/62223) | Update dependencies |
| 0.0.24 | 2025-06-14 | [60069](https://github.com/airbytehq/airbyte/pull/60069) | Update dependencies |
| 0.0.23 | 2025-05-04 | [59589](https://github.com/airbytehq/airbyte/pull/59589) | Update dependencies |
| 0.0.22 | 2025-04-27 | [58963](https://github.com/airbytehq/airbyte/pull/58963) | Update dependencies |
| 0.0.21 | 2025-04-19 | [58432](https://github.com/airbytehq/airbyte/pull/58432) | Update dependencies |
| 0.0.20 | 2025-04-12 | [57982](https://github.com/airbytehq/airbyte/pull/57982) | Update dependencies |
| 0.0.19 | 2025-04-05 | [57486](https://github.com/airbytehq/airbyte/pull/57486) | Update dependencies |
| 0.0.18 | 2025-03-29 | [56848](https://github.com/airbytehq/airbyte/pull/56848) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56281](https://github.com/airbytehq/airbyte/pull/56281) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55575](https://github.com/airbytehq/airbyte/pull/55575) | Update dependencies |
| 0.0.15 | 2025-03-01 | [55085](https://github.com/airbytehq/airbyte/pull/55085) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54471](https://github.com/airbytehq/airbyte/pull/54471) | Update dependencies |
| 0.0.13 | 2025-02-15 | [53553](https://github.com/airbytehq/airbyte/pull/53553) | Update dependencies |
| 0.0.12 | 2025-02-01 | [53054](https://github.com/airbytehq/airbyte/pull/53054) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52452](https://github.com/airbytehq/airbyte/pull/52452) | Update dependencies |
| 0.0.10 | 2025-01-18 | [52022](https://github.com/airbytehq/airbyte/pull/52022) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51435](https://github.com/airbytehq/airbyte/pull/51435) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50792](https://github.com/airbytehq/airbyte/pull/50792) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50312](https://github.com/airbytehq/airbyte/pull/50312) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49741](https://github.com/airbytehq/airbyte/pull/49741) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49398](https://github.com/airbytehq/airbyte/pull/49398) | Update dependencies |
| 0.0.4 | 2024-11-04 | [48315](https://github.com/airbytehq/airbyte/pull/48315) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47815](https://github.com/airbytehq/airbyte/pull/47815) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47612](https://github.com/airbytehq/airbyte/pull/47612) | Update dependencies |
| 0.0.1 | 2024-10-22 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
