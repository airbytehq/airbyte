# AWIN Advertiser
Website: https://www.awin.com/
Documentation: https://developer.awin.com/apidocs/for-advertisers

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `advertiserId` | `string` | advertiserId.  |  |
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaign_performance | date.publisherId.campaign | No pagination | ✅ |  ❌  |
| transactions | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-04-24 | | Initial release by [@ryanmcg2203](https://github.com/ryanmcg2203) via Connector Builder |

</details>
