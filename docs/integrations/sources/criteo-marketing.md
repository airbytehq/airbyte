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
| 0.0.4 | 2026-04-28 | [77215](https://github.com/airbytehq/airbyte/pull/77215) | Update dependencies |
| 0.0.3 | 2026-04-21 | [75099](https://github.com/airbytehq/airbyte/pull/75099) | Update dependencies |
| 0.0.2 | 2026-03-03 | [74165](https://github.com/airbytehq/airbyte/pull/74165) | Update dependencies |
| 0.0.1 | 2026-02-04 | | Initial release by [@mvfc](https://github.com/mvfc) via Connector Builder |

</details>
