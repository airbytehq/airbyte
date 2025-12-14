# Dwolla
Website: https://dashboard.dwolla.com/
API Reference: https://developers.dwolla.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `environment` | `string` | Environment. The environment for the Dwolla API, either &#39;api-sandbox&#39; or &#39;api&#39;. | api |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ✅  |
| funding_sources | id | DefaultPaginator | ✅ |  ✅  |
| events | id | DefaultPaginator | ✅ |  ✅  |
| exchange_partners | id | DefaultPaginator | ✅ |  ✅  |
| business-classifications | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.26 | 2025-12-09 | [70541](https://github.com/airbytehq/airbyte/pull/70541) | Update dependencies |
| 0.0.25 | 2025-11-25 | [70175](https://github.com/airbytehq/airbyte/pull/70175) | Update dependencies |
| 0.0.24 | 2025-11-18 | [69362](https://github.com/airbytehq/airbyte/pull/69362) | Update dependencies |
| 0.0.23 | 2025-10-29 | [68701](https://github.com/airbytehq/airbyte/pull/68701) | Update dependencies |
| 0.0.22 | 2025-10-21 | [68564](https://github.com/airbytehq/airbyte/pull/68564) | Update dependencies |
| 0.0.21 | 2025-10-14 | [67728](https://github.com/airbytehq/airbyte/pull/67728) | Update dependencies |
| 0.0.20 | 2025-10-07 | [67276](https://github.com/airbytehq/airbyte/pull/67276) | Update dependencies |
| 0.0.19 | 2025-09-30 | [65801](https://github.com/airbytehq/airbyte/pull/65801) | Update dependencies |
| 0.0.18 | 2025-08-23 | [65237](https://github.com/airbytehq/airbyte/pull/65237) | Update dependencies |
| 0.0.17 | 2025-08-09 | [64726](https://github.com/airbytehq/airbyte/pull/64726) | Update dependencies |
| 0.0.16 | 2025-08-02 | [64376](https://github.com/airbytehq/airbyte/pull/64376) | Update dependencies |
| 0.0.15 | 2025-07-26 | [64033](https://github.com/airbytehq/airbyte/pull/64033) | Update dependencies |
| 0.0.14 | 2025-07-19 | [63583](https://github.com/airbytehq/airbyte/pull/63583) | Update dependencies |
| 0.0.13 | 2025-07-12 | [62966](https://github.com/airbytehq/airbyte/pull/62966) | Update dependencies |
| 0.0.12 | 2025-07-05 | [62777](https://github.com/airbytehq/airbyte/pull/62777) | Update dependencies |
| 0.0.11 | 2025-06-28 | [62331](https://github.com/airbytehq/airbyte/pull/62331) | Update dependencies |
| 0.0.10 | 2025-06-21 | [61968](https://github.com/airbytehq/airbyte/pull/61968) | Update dependencies |
| 0.0.9 | 2025-06-14 | [61221](https://github.com/airbytehq/airbyte/pull/61221) | Update dependencies |
| 0.0.8 | 2025-05-24 | [60423](https://github.com/airbytehq/airbyte/pull/60423) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60041](https://github.com/airbytehq/airbyte/pull/60041) | Update dependencies |
| 0.0.6 | 2025-05-03 | [59414](https://github.com/airbytehq/airbyte/pull/59414) | Update dependencies |
| 0.0.5 | 2025-04-26 | [58870](https://github.com/airbytehq/airbyte/pull/58870) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58303](https://github.com/airbytehq/airbyte/pull/58303) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57769](https://github.com/airbytehq/airbyte/pull/57769) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57266](https://github.com/airbytehq/airbyte/pull/57266) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57004](https://github.com/airbytehq/airbyte/pull/57004) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
