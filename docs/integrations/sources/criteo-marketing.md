# Criteo Marketing
API documentation:

https://developers.criteo.com/marketing-solutions/reference/getadsetreport

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `currency` | `string` | Currency. Currency to be used on the report |  |
| `end_date` | `string` | EndDate. End date of the report |  |
| `client_id` | `string` | OAuth Client ID.  |  |
| `start_date` | `string` | StartDate. Start date of the report |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| ad_spend_daily | AdvertiserId.CampaignId.Day | No pagination | ✅ |  ✅  |
| adsets | Id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-02-04 | | Initial release by [@mvfc](https://github.com/mvfc) via Connector Builder |

</details>
