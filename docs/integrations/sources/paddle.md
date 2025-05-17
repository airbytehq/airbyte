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
| 0.0.8 | 2025-05-17 | [60485](https://github.com/airbytehq/airbyte/pull/60485) | Update dependencies |
| 0.0.7 | 2025-05-10 | [60059](https://github.com/airbytehq/airbyte/pull/60059) | Update dependencies |
| 0.0.6 | 2025-05-04 | [59518](https://github.com/airbytehq/airbyte/pull/59518) | Update dependencies |
| 0.0.5 | 2025-04-27 | [59085](https://github.com/airbytehq/airbyte/pull/59085) | Update dependencies |
| 0.0.4 | 2025-04-19 | [58515](https://github.com/airbytehq/airbyte/pull/58515) | Update dependencies |
| 0.0.3 | 2025-04-12 | [57847](https://github.com/airbytehq/airbyte/pull/57847) | Update dependencies |
| 0.0.2 | 2025-04-05 | [57338](https://github.com/airbytehq/airbyte/pull/57338) | Update dependencies |
| 0.0.1 | 2025-04-04 | [57003](https://github.com/airbytehq/airbyte/pull/57003) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
