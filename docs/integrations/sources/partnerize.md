# Partnerize
Website: https://console.partnerize.com/
Documentation: https://api-docs.partnerize.com/partner/#section/Introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `user_api_key` | `string` | User API Key. The user API key identifies the user on whose behalf the request is made. Find it in your account settings under &#39;User API Key&#39; at https://console.partnerize.com. |  |
| `application_key` | `string` | Application Key. The application key identifies the network you are making the request against. Find it in your account settings under &#39;User Application Key&#39; at https://console.partnerize.com. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| countries | ref_country_id | DefaultPaginator | ✅ |  ❌  |
| currencies | currency_id | DefaultPaginator | ✅ |  ❌  |
| devices | ref_device_id | DefaultPaginator | ✅ |  ❌  |
| timezones | ref_timezone_id | DefaultPaginator | ✅ |  ❌  |
| traffic_sources | ref_traffic_source_id | DefaultPaginator | ✅ |  ❌  |
| user_context | ref_user_context_id | DefaultPaginator | ✅ |  ❌  |
| conversion_type | conversion_type_id | DefaultPaginator | ✅ |  ❌  |
| conversion_metrics | ref_conversion_metric_id | DefaultPaginator | ✅ |  ❌  |
| partnership_model | ref_partnership_model_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.27 | 2025-12-09 | [70479](https://github.com/airbytehq/airbyte/pull/70479) | Update dependencies |
| 0.0.26 | 2025-11-25 | [70086](https://github.com/airbytehq/airbyte/pull/70086) | Update dependencies |
| 0.0.25 | 2025-11-18 | [69696](https://github.com/airbytehq/airbyte/pull/69696) | Update dependencies |
| 0.0.24 | 2025-10-29 | [69014](https://github.com/airbytehq/airbyte/pull/69014) | Update dependencies |
| 0.0.23 | 2025-10-21 | [68284](https://github.com/airbytehq/airbyte/pull/68284) | Update dependencies |
| 0.0.22 | 2025-10-14 | [67730](https://github.com/airbytehq/airbyte/pull/67730) | Update dependencies |
| 0.0.21 | 2025-10-07 | [67338](https://github.com/airbytehq/airbyte/pull/67338) | Update dependencies |
| 0.0.20 | 2025-09-30 | [66376](https://github.com/airbytehq/airbyte/pull/66376) | Update dependencies |
| 0.0.19 | 2025-09-09 | [65778](https://github.com/airbytehq/airbyte/pull/65778) | Update dependencies |
| 0.0.18 | 2025-08-23 | [65196](https://github.com/airbytehq/airbyte/pull/65196) | Update dependencies |
| 0.0.17 | 2025-08-16 | [64968](https://github.com/airbytehq/airbyte/pull/64968) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64261](https://github.com/airbytehq/airbyte/pull/64261) | Update dependencies |
| 0.0.15 | 2025-07-26 | [63886](https://github.com/airbytehq/airbyte/pull/63886) | Update dependencies |
| 0.0.14 | 2025-07-19 | [63418](https://github.com/airbytehq/airbyte/pull/63418) | Update dependencies |
| 0.0.13 | 2025-07-12 | [63265](https://github.com/airbytehq/airbyte/pull/63265) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62634](https://github.com/airbytehq/airbyte/pull/62634) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62416](https://github.com/airbytehq/airbyte/pull/62416) | Update dependencies |
| 0.0.10 | 2025-06-21 | [61886](https://github.com/airbytehq/airbyte/pull/61886) | Update dependencies |
| 0.0.9 | 2025-06-14 | [61051](https://github.com/airbytehq/airbyte/pull/61051) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60499](https://github.com/airbytehq/airbyte/pull/60499) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60131](https://github.com/airbytehq/airbyte/pull/60131) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59523](https://github.com/airbytehq/airbyte/pull/59523) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59109](https://github.com/airbytehq/airbyte/pull/59109) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58492](https://github.com/airbytehq/airbyte/pull/58492) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57896](https://github.com/airbytehq/airbyte/pull/57896) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57303](https://github.com/airbytehq/airbyte/pull/57303) | Update dependencies |
| 0.0.1 | 2025-03-31 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
