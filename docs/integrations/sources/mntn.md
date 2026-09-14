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
| 0.0.7 | 2026-09-08 | [85583](https://github.com/airbytehq/airbyte/pull/85583) | Update dependencies |
| 0.0.6 | 2026-08-25 | [85027](https://github.com/airbytehq/airbyte/pull/85027) | Enable acceptance test suite with GSM test secrets |
| 0.0.5 | 2026-08-18 | [84647](https://github.com/airbytehq/airbyte/pull/84647) | Update dependencies |
| 0.0.4 | 2026-08-11 | [84027](https://github.com/airbytehq/airbyte/pull/84027) | Update dependencies |
| 0.0.3 | 2026-08-04 | [83541](https://github.com/airbytehq/airbyte/pull/83541) | Update dependencies |
| 0.0.2 | 2026-07-28 | [83005](https://github.com/airbytehq/airbyte/pull/83005) | Update dependencies |
| 0.0.1 | 2026-06-30 | [81334](https://github.com/airbytehq/airbyte/pull/81334) | Initial release by [@Ella6882](https://github.com/Ella6882) via Connector Builder |

</details>
