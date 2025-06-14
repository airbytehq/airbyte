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
| 0.0.8 | 2025-06-14 | [61077](https://github.com/airbytehq/airbyte/pull/61077) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60595](https://github.com/airbytehq/airbyte/pull/60595) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59861](https://github.com/airbytehq/airbyte/pull/59861) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59285](https://github.com/airbytehq/airbyte/pull/59285) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58769](https://github.com/airbytehq/airbyte/pull/58769) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58155](https://github.com/airbytehq/airbyte/pull/58155) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57687](https://github.com/airbytehq/airbyte/pull/57687) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57529](https://github.com/airbytehq/airbyte/pull/57529) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
