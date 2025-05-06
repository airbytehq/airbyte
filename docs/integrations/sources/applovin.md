# AppLovin
A lightweight, declarative Airbyte source that pulls your Applovin advertiser report via the /report endpoint into a single report stream. It requests data by date range (start_date → now), automatically re-fetching the prior 2 days on each run (lookback window = P2D) to capture any late-arriving hourly rows. Records are deduplicated in the destination using a composite primary key (ad_id, campaign_id_external, creative_set_id, day, hour, placement_type, platform). All hourly metrics (cost, clicks, ROAS, etc.) flow through the results array via a simple DpathExtractor, enabling both full historical backfills and efficient daily incremental loads with zero data loss.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| report | ad_id.campaign_id_external.creative_set_id.day.hour.placement_type.platform | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-05-06 | | Initial release by [@CtrlAltDeploy](https://github.com/CtrlAltDeploy) via Connector Builder |

</details>
