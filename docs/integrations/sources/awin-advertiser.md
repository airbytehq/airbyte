# AWIN Advertiser
Website: https://www.awin.com/
Documentation: https://developer.awin.com/apidocs/for-advertisers

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `advertiserId` | `string` | advertiserId.  |  |
| `api_key` | `string` | API Key.  |  |
| `step_increment` | `string` | Step Increment. ISO8601 duration format like &#39;P400D&#39; | P400D |
| `lookback_days` | `integer` | Lookback Days. Number of days to re-fetch on each sync. |  |
| `start_date_campaigns` | `string` | Start Date Campaigns. Accepts &#39;YYYY-MM-DD&#39; |  |
| `start_date_transactions` | `string` | Start Date Transactions. Accepts &#39;YYYY-MM-DDTHH:MM:SS&#39; |  |

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
| 0.0.1 | 2025-04-28 | | Initial release by [@ryanmcg2203](https://github.com/ryanmcg2203) via Connector Builder |

</details>
