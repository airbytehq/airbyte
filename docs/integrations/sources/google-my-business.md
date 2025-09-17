# Google My Business
The Google My Business Metrics connector enables users to efficiently synchronize key performance metrics from Google My Business accounts into their data destination. This connector retrieves data such as views, clicks, calls, reviews, and user interactions, allowing for streamlined analytics, reporting, and integration into broader business intelligence workflows.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID. Google OAuth Client ID |  |
| `client_secret` | `string` | Client Secret. Google OAuth Client Secret |  |
| `refresh_token` | `string` | Refresh Token. Google OAuth Refresh Token |  |
| `location_ids` | `array` | Location IDs. List of Google My Business location IDs |  |
| `daily_metrics` | `array` | Daily Metrics. List of daily metrics to fetch | [WEBSITE_CLICKS] |
| `start_date` | `string` | Start Date. Start date for data extraction |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| BusinessMetrics |  | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-08-06 | | Initial release by [@samuelperezh](https://github.com/samuelperezh) via Connector Builder |

</details>
