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
