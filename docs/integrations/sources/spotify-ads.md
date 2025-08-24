# Spotify Ads

Spotify Ads Connector
Extract campaign performance data from Spotify&#39;s advertising platform
This connector syncs advertising data from Spotify&#39;s Partner API, enabling you to analyze campaign performance metrics and optimize your Spotify advertising strategy. Perfect for marketers, agencies, and businesses running audio and video advertising campaigns on Spotify.
Available Data

Ad Accounts: Basic account information and settings
Campaigns: Campaign details, names, and status
Campaign Performance: Daily metrics including:

Standard metrics: impressions, clicks, spend, CTR, reach, frequency
Audio-specific: streams, listeners, new listeners, paid listens
Video metrics: video views, expands, completion rates
Advanced: conversion rates, intent rates, frequency metrics



Requirements

Spotify Developer application with Partner API access
OAuth 2.0 credentials (Client ID, Client Secret, Refresh Token)
Valid Spotify Ad Account ID

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID. The Client ID of your Spotify Developer application. |  |
| `client_secret` | `string` | Client Secret. The Client Secret of your Spotify Developer application. |  |
| `refresh_token` | `string` | Refresh Token. The Refresh Token obtained from the initial OAuth 2.0 authorization flow. |  |
| `ad_account_id` | `string` | Ad Account ID. The ID of the Spotify Ad Account you want to sync data from. |  |
| `start_date` | `string` | Start Date. The date to start syncing data from, in YYYY-MM-DD format. |  |
| `fields` | `array` | Report Fields. List of fields to include in the campaign performance report. Choose from available metrics. | [IMPRESSIONS, CLICKS, SPEND, CTR, REACH, FREQUENCY, COMPLETION_RATE] |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| ad_accounts | id | No pagination | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| campaign_performance | day.campaign_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-08-24 | [65466](https://github.com/airbytehq/airbyte/pull/65466) | Update dependencies |
| 0.0.7 | 2025-08-09 | [64817](https://github.com/airbytehq/airbyte/pull/64817) | Update dependencies |
| 0.0.6 | 2025-08-02 | [64468](https://github.com/airbytehq/airbyte/pull/64468) | Update dependencies |
| 0.0.5 | 2025-07-12 | [63080](https://github.com/airbytehq/airbyte/pull/63080) | Update dependencies |
| 0.0.4 | 2025-07-05 | [62741](https://github.com/airbytehq/airbyte/pull/62741) | Update dependencies |
| 0.0.3 | 2025-06-28 | [62277](https://github.com/airbytehq/airbyte/pull/62277) | Update dependencies |
| 0.0.2 | 2025-06-21 | [61807](https://github.com/airbytehq/airbyte/pull/61807) | Update dependencies |
| 0.0.1 | 2025-06-16 | | Initial release by [@Magistah](https://github.com/Magistah) via Connector Builder |

</details>
