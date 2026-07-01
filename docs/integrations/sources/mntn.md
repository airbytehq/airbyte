# MNTN
MNTN is a platform that lets brands of any size create and launch TV commercials on shows, movies, and live sports.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_time` | `string` | start_time.  | 2023-01-01 |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| CampaignDetails | ID | No pagination | ✅ |  ❌  |
| CreativeDetails | ID.Day | No pagination | ✅ |  ✅  |
| Campaign | ID.Day | No pagination | ✅ |  ✅  |
| Creative | ID.Day | No pagination | ✅ |  ✅  |
| Advertiser | ID.Day | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-06-30 | | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
