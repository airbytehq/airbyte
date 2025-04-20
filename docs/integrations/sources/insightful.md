# Insightful
Website: https://app.insightful.io/
API Reference: https://developers.insightful.io/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. Your API token for accessing the Insightful API. Generate it by logging in as an Admin to your organization&#39;s account, navigating to the API page, and creating a new token. Note that this token will only be shown once, so store it securely. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| employee | id | DefaultPaginator | ✅ |  ✅  |
| team | id | DefaultPaginator | ✅ |  ❌  |
| shared-settings | id | DefaultPaginator | ✅ |  ✅  |
| projects | id | DefaultPaginator | ✅ |  ✅  |
| tags | id | DefaultPaginator | ✅ |  ✅  |
| app-category | id | DefaultPaginator | ✅ |  ❌  |
| directory | id | DefaultPaginator | ✅ |  ✅  |
| scheduled-shift-settings | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58155](https://github.com/airbytehq/airbyte/pull/58155) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57687](https://github.com/airbytehq/airbyte/pull/57687) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57529](https://github.com/airbytehq/airbyte/pull/57529) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
