# Straddle
Website: https://dashboard.straddle.io/
API Reference: https://straddle.dev/api-reference

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your secret API key for authenticating with the Straddle API. Generate it from the Straddle Dashboard under Developers &gt; API Keys. Use separate keys for Sandbox and Production environments. |  |
| `environment` | `string` | Environment. The environment for the API (e.g., &#39;sandbox&#39; or &#39;production&#39;) | production |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | id | DefaultPaginator | ✅ |  ✅  |
| organizations | id | DefaultPaginator | ✅ |  ✅  |
| accounts | id | DefaultPaginator | ✅ |  ✅  |
| representatives | id | DefaultPaginator | ✅ |  ✅  |
| capability_requests | id | DefaultPaginator | ✅ |  ✅  |
| linked_bank_accounts | id | DefaultPaginator | ✅ |  ✅  |
| customer_review_customer_details | id | DefaultPaginator | ✅ |  ✅  |
| customer_review_identity_details | review_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-10 | [57559](https://github.com/airbytehq/airbyte/pull/57559) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
