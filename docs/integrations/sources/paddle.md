# Paddle
Website: https://www.paddle.com/
API Reference: https://developer.paddle.com/api-reference/overview

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your Paddle API key. You can generate it by navigating to Paddle &gt; Developer tools &gt; Authentication &gt; Generate API key. Treat this key like a password and keep it secure. |  |
| `environment` | `string` | Environment. The environment for the Paddle API, either &#39;sandbox&#39; or &#39;live&#39;. | api |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| adjustments | id | DefaultPaginator | ✅ |  ✅  |
| customers | id | DefaultPaginator | ✅ |  ✅  |
| customer_addresses | id | DefaultPaginator | ✅ |  ✅  |
| discounts | id | DefaultPaginator | ✅ |  ✅  |
| prices | id | DefaultPaginator | ✅ |  ✅  |
| products | id | DefaultPaginator | ✅ |  ✅  |
| businesses | id | DefaultPaginator | ✅ |  ✅  |
| events | event_id | DefaultPaginator | ✅ |  ✅  |
| event_types | uuid | DefaultPaginator | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ✅  |
| ip_addresses | uuid | DefaultPaginator | ✅ |  ❌  |
| subscriptions | id | DefaultPaginator | ✅ |  ✅  |
| transactions | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.2.11 | 2025-12-09 | [70506](https://github.com/airbytehq/airbyte/pull/70506) | Update dependencies |
| 0.2.10 | 2025-11-25 | [70089](https://github.com/airbytehq/airbyte/pull/70089) | Update dependencies |
| 0.2.9 | 2025-11-18 | [69694](https://github.com/airbytehq/airbyte/pull/69694) | Update dependencies |
| 0.2.8 | 2025-10-29 | [69016](https://github.com/airbytehq/airbyte/pull/69016) | Update dependencies |
| 0.2.7 | 2025-10-21 | [68291](https://github.com/airbytehq/airbyte/pull/68291) | Update dependencies |
| 0.2.6 | 2025-10-14 | [67785](https://github.com/airbytehq/airbyte/pull/67785) | Update dependencies |
| 0.2.5 | 2025-10-07 | [67336](https://github.com/airbytehq/airbyte/pull/67336) | Update dependencies |
| 0.2.4 | 2025-09-30 | [66390](https://github.com/airbytehq/airbyte/pull/66390) | Update dependencies |
| 0.2.3 | 2025-09-09 | [65806](https://github.com/airbytehq/airbyte/pull/65806) | Update dependencies |
| 0.2.2 | 2025-08-23 | [65194](https://github.com/airbytehq/airbyte/pull/65194) | Update dependencies |
| 0.2.1 | 2025-08-09 | [64749](https://github.com/airbytehq/airbyte/pull/64749) | Update dependencies |
| 0.2.0 | 2025-07-10 | [62891](https://github.com/airbytehq/airbyte/pull/62891) | Remove `custom_data` property constraints and add it to `customers` stream |
| 0.1.5 | 2025-08-02 | [64300](https://github.com/airbytehq/airbyte/pull/64300) | Update dependencies |
| 0.1.4 | 2025-07-26 | [63842](https://github.com/airbytehq/airbyte/pull/63842) | Update dependencies |
| 0.1.3 | 2025-07-19 | [63388](https://github.com/airbytehq/airbyte/pull/63388) | Update dependencies |
| 0.1.2 | 2025-07-12 | [63195](https://github.com/airbytehq/airbyte/pull/63195) | Update dependencies |
| 0.1.1 | 2025-07-05 | [62566](https://github.com/airbytehq/airbyte/pull/62566) | Update dependencies |
| 0.1.0 | 2025-07-01 | [62479](https://github.com/airbytehq/airbyte/pull/62479) | Add adjustments stream |
| 0.0.11 | 2025-07-01 | [62461](https://github.com/airbytehq/airbyte/pull/62461) | Add constant retry backoff per Paddle API Docs |
| 0.0.10 | 2025-06-28 | [62318](https://github.com/airbytehq/airbyte/pull/62318) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61917](https://github.com/airbytehq/airbyte/pull/61917) | Update dependencies |
| 0.0.8 | 2025-06-14 | [60485](https://github.com/airbytehq/airbyte/pull/60485) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60059](https://github.com/airbytehq/airbyte/pull/60059) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59518](https://github.com/airbytehq/airbyte/pull/59518) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59085](https://github.com/airbytehq/airbyte/pull/59085) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58515](https://github.com/airbytehq/airbyte/pull/58515) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57847](https://github.com/airbytehq/airbyte/pull/57847) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57338](https://github.com/airbytehq/airbyte/pull/57338) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57003](https://github.com/airbytehq/airbyte/pull/57003) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
