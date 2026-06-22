# Criteo Marketing
API documentation:

https://developers.criteo.com/marketing-solutions/reference/getadsetreport

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `advertiser_ids` | `string` | Advertiser IDs. The comma-separated list of advertiser IDs to include in the statistics report. |  |
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

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.1.0 | 2026-06-22 | [XXXXX](https://github.com/airbytehq/airbyte/pull/XXXXX) | Add required `advertiser_ids` config field to fix broken `ad_spend_daily` stream |
| 0.0.7 | 2026-06-16 | [79780](https://github.com/airbytehq/airbyte/pull/79780) | Update dependencies |
| 0.0.6 | 2026-06-09 | [79277](https://github.com/airbytehq/airbyte/pull/79277) | Update dependencies |
| 0.0.5 | 2026-06-02 | [78651](https://github.com/airbytehq/airbyte/pull/78651) | Update dependencies |
| 0.0.4 | 2026-04-28 | [77215](https://github.com/airbytehq/airbyte/pull/77215) | Update dependencies |
| 0.0.3 | 2026-04-21 | [75099](https://github.com/airbytehq/airbyte/pull/75099) | Update dependencies |
| 0.0.2 | 2026-03-03 | [74165](https://github.com/airbytehq/airbyte/pull/74165) | Update dependencies |
| 0.0.1 | 2026-02-04 | | Initial release by [@mvfc](https://github.com/mvfc) via Connector Builder |

</details>
