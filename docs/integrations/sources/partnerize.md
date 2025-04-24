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
| 0.0.4 | 2025-04-19 | [58492](https://github.com/airbytehq/airbyte/pull/58492) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57896](https://github.com/airbytehq/airbyte/pull/57896) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57303](https://github.com/airbytehq/airbyte/pull/57303) | Update dependencies |
| 0.0.1 | 2025-03-31 | | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
