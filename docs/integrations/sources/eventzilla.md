# Eventzilla
The Airbyte connector for Eventzilla enables seamless integration between Eventzilla and various data destinations. It automates the extraction of event management data, such as attendee details, ticket sales, and event performance metrics, and syncs it with your preferred data warehouses or analytics tools. This connector helps organizations centralize and analyze their Eventzilla data for reporting, monitoring, and strategic insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `x-api-key` | `string` | API Key. API key to use. Generate it by creating a new application within your Eventzilla account settings under Settings &gt; App Management. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ❌  |
| attendees | id | DefaultPaginator | ✅ |  ❌  |
| categories |  | DefaultPaginator | ✅ |  ❌  |
| tickets | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| transactions | refno | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.38 | 2025-12-09 | [70579](https://github.com/airbytehq/airbyte/pull/70579) | Update dependencies |
| 0.0.37 | 2025-11-25 | [70167](https://github.com/airbytehq/airbyte/pull/70167) | Update dependencies |
| 0.0.36 | 2025-11-18 | [69361](https://github.com/airbytehq/airbyte/pull/69361) | Update dependencies |
| 0.0.35 | 2025-10-29 | [68743](https://github.com/airbytehq/airbyte/pull/68743) | Update dependencies |
| 0.0.34 | 2025-10-21 | [68550](https://github.com/airbytehq/airbyte/pull/68550) | Update dependencies |
| 0.0.33 | 2025-10-14 | [67793](https://github.com/airbytehq/airbyte/pull/67793) | Update dependencies |
| 0.0.32 | 2025-10-07 | [67284](https://github.com/airbytehq/airbyte/pull/67284) | Update dependencies |
| 0.0.31 | 2025-09-30 | [65852](https://github.com/airbytehq/airbyte/pull/65852) | Update dependencies |
| 0.0.30 | 2025-08-23 | [65271](https://github.com/airbytehq/airbyte/pull/65271) | Update dependencies |
| 0.0.29 | 2025-08-09 | [64691](https://github.com/airbytehq/airbyte/pull/64691) | Update dependencies |
| 0.0.28 | 2025-08-02 | [64336](https://github.com/airbytehq/airbyte/pull/64336) | Update dependencies |
| 0.0.27 | 2025-07-26 | [64013](https://github.com/airbytehq/airbyte/pull/64013) | Update dependencies |
| 0.0.26 | 2025-07-19 | [63603](https://github.com/airbytehq/airbyte/pull/63603) | Update dependencies |
| 0.0.25 | 2025-07-12 | [62980](https://github.com/airbytehq/airbyte/pull/62980) | Update dependencies |
| 0.0.24 | 2025-07-05 | [62818](https://github.com/airbytehq/airbyte/pull/62818) | Update dependencies |
| 0.0.23 | 2025-06-28 | [62404](https://github.com/airbytehq/airbyte/pull/62404) | Update dependencies |
| 0.0.22 | 2025-06-22 | [62005](https://github.com/airbytehq/airbyte/pull/62005) | Update dependencies |
| 0.0.21 | 2025-06-14 | [61185](https://github.com/airbytehq/airbyte/pull/61185) | Update dependencies |
| 0.0.20 | 2025-05-24 | [59450](https://github.com/airbytehq/airbyte/pull/59450) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58333](https://github.com/airbytehq/airbyte/pull/58333) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57782](https://github.com/airbytehq/airbyte/pull/57782) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57205](https://github.com/airbytehq/airbyte/pull/57205) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56539](https://github.com/airbytehq/airbyte/pull/56539) | Update dependencies |
| 0.0.15 | 2025-03-22 | [55959](https://github.com/airbytehq/airbyte/pull/55959) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55334](https://github.com/airbytehq/airbyte/pull/55334) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54927](https://github.com/airbytehq/airbyte/pull/54927) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54450](https://github.com/airbytehq/airbyte/pull/54450) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53753](https://github.com/airbytehq/airbyte/pull/53753) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53375](https://github.com/airbytehq/airbyte/pull/53375) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52840](https://github.com/airbytehq/airbyte/pull/52840) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52334](https://github.com/airbytehq/airbyte/pull/52334) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51675](https://github.com/airbytehq/airbyte/pull/51675) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51083](https://github.com/airbytehq/airbyte/pull/51083) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50549](https://github.com/airbytehq/airbyte/pull/50549) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50047](https://github.com/airbytehq/airbyte/pull/50047) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49488](https://github.com/airbytehq/airbyte/pull/49488) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49198](https://github.com/airbytehq/airbyte/pull/49198) | Update dependencies |
| 0.0.1 | 2024-10-23 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
