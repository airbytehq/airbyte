# AWIN Advertiser
Website: https://www.awin.com/
Documentation: https://developer.awin.com/apidocs/for-advertisers

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `advertiserId` | `string` | advertiserId. Your Awin Advertiser ID. You can find this in your Awin dashboard or account settings. |  |
| `api_key` | `string` | API Key. Your Awin API key. Generate this from your Awin account under API Credentials. |  |
| `step_increment` | `string` | Step Increment. The time window size for each API request in ISO8601 duration format. For the campaign performance stream, Awin API explicitly limits the period between startDate and endDate to 400 days maximum.  | P400D |
| `lookback_days` | `integer` | Lookback Days. Number of days to look back on each sync to catch any updates to existing records. |  |
| `start_date` | `string` | Start Date. Start date for data replication in YYYY-MM-DD format |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaign_performance | date.publisherId.campaign | No pagination | ✅ |  ✅  |
| transactions | id | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.14 | 2025-12-09 | [70790](https://github.com/airbytehq/airbyte/pull/70790) | Update dependencies |
| 0.0.13 | 2025-11-25 | [69874](https://github.com/airbytehq/airbyte/pull/69874) | Update dependencies |
| 0.0.12 | 2025-11-18 | [69520](https://github.com/airbytehq/airbyte/pull/69520) | Update dependencies |
| 0.0.11 | 2025-10-29 | [68899](https://github.com/airbytehq/airbyte/pull/68899) | Update dependencies |
| 0.0.10 | 2025-10-21 | [68381](https://github.com/airbytehq/airbyte/pull/68381) | Update dependencies |
| 0.0.9 | 2025-10-14 | [68006](https://github.com/airbytehq/airbyte/pull/68006) | Update dependencies |
| 0.0.8 | 2025-10-07 | [67167](https://github.com/airbytehq/airbyte/pull/67167) | Update dependencies |
| 0.0.7 | 2025-09-30 | [65646](https://github.com/airbytehq/airbyte/pull/65646) | Update dependencies |
| 0.0.6 | 2025-08-09 | [64645](https://github.com/airbytehq/airbyte/pull/64645) | Update dependencies |
| 0.0.5 | 2025-08-02 | [64430](https://github.com/airbytehq/airbyte/pull/64430) | Update dependencies |
| 0.0.4 | 2025-06-25 | [62059](https://github.com/airbytehq/airbyte/pull/62059) | source-awin-advertiser contribution from navneetmaharishi |
| 0.0.3 | 2025-06-21 | [60733](https://github.com/airbytehq/airbyte/pull/60733) | Update dependencies |
| 0.0.2 | 2025-05-10 | [59902](https://github.com/airbytehq/airbyte/pull/59902) | Update dependencies |
| 0.0.1 | 2025-04-29 | | Initial release by [@ryanmcg2203](https://github.com/ryanmcg2203) via Connector Builder |

</details>
