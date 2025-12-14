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
| 0.0.26 | 2025-12-09 | [70491](https://github.com/airbytehq/airbyte/pull/70491) | Update dependencies |
| 0.0.25 | 2025-11-25 | [70164](https://github.com/airbytehq/airbyte/pull/70164) | Update dependencies |
| 0.0.24 | 2025-11-18 | [69547](https://github.com/airbytehq/airbyte/pull/69547) | Update dependencies |
| 0.0.23 | 2025-10-29 | [68792](https://github.com/airbytehq/airbyte/pull/68792) | Update dependencies |
| 0.0.22 | 2025-10-21 | [68476](https://github.com/airbytehq/airbyte/pull/68476) | Update dependencies |
| 0.0.21 | 2025-10-14 | [67957](https://github.com/airbytehq/airbyte/pull/67957) | Update dependencies |
| 0.0.20 | 2025-10-07 | [67362](https://github.com/airbytehq/airbyte/pull/67362) | Update dependencies |
| 0.0.19 | 2025-09-30 | [66792](https://github.com/airbytehq/airbyte/pull/66792) | Update dependencies |
| 0.0.18 | 2025-09-09 | [66075](https://github.com/airbytehq/airbyte/pull/66075) | Update dependencies |
| 0.0.17 | 2025-08-23 | [65330](https://github.com/airbytehq/airbyte/pull/65330) | Update dependencies |
| 0.0.16 | 2025-08-09 | [64632](https://github.com/airbytehq/airbyte/pull/64632) | Update dependencies |
| 0.0.15 | 2025-08-02 | [64238](https://github.com/airbytehq/airbyte/pull/64238) | Update dependencies |
| 0.0.14 | 2025-07-26 | [63828](https://github.com/airbytehq/airbyte/pull/63828) | Update dependencies |
| 0.0.13 | 2025-07-19 | [63497](https://github.com/airbytehq/airbyte/pull/63497) | Update dependencies |
| 0.0.12 | 2025-07-12 | [63101](https://github.com/airbytehq/airbyte/pull/63101) | Update dependencies |
| 0.0.11 | 2025-07-05 | [62561](https://github.com/airbytehq/airbyte/pull/62561) | Update dependencies |
| 0.0.10 | 2025-06-28 | [62196](https://github.com/airbytehq/airbyte/pull/62196) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61869](https://github.com/airbytehq/airbyte/pull/61869) | Update dependencies |
| 0.0.8 | 2025-06-14 | [61077](https://github.com/airbytehq/airbyte/pull/61077) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60595](https://github.com/airbytehq/airbyte/pull/60595) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59861](https://github.com/airbytehq/airbyte/pull/59861) | Update dependencies |
| 0.0.5 | 2025-05-03 | [59285](https://github.com/airbytehq/airbyte/pull/59285) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58769](https://github.com/airbytehq/airbyte/pull/58769) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58155](https://github.com/airbytehq/airbyte/pull/58155) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57687](https://github.com/airbytehq/airbyte/pull/57687) | Update dependencies |
| 0.0.1 | 2025-04-09 | [57529](https://github.com/airbytehq/airbyte/pull/57529) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
