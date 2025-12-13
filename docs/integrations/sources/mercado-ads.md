# Mercado Ads
Get ad analytics from all Mercado Ads placements

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `lookback_days` | `number` | Lookback Days.  | 7 |
| `start_date` | `string` | Start Date. Cannot exceed 90 days from current day for Product Ads, and 90 days from &quot;End Date&quot; on Brand and Display Ads |  |
| `end_date` | `string` | End Date. Cannot exceed 90 days from current day for Product Ads |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| brand_advertisers | advertiser_id | No pagination | ✅ |  ❌  |
| brand_campaigns | advertiser_id.campaign_id | No pagination | ✅ |  ❌  |
| brand_campaigns_metrics | date.advertiser_id.campaign_id | DefaultPaginator | ✅ |  ✅  |
| brand_items | advertiser_id.campaign_id.item_id | No pagination | ✅ |  ❌  |
| brand_keywords | advertiser_id.campaign_id.term.match_type | No pagination | ✅ |  ❌  |
| brand_keywords_metrics | date.advertiser_id.campaign_id | DefaultPaginator | ✅ |  ✅  |
| display_advertisers | advertiser_id | No pagination | ✅ |  ❌  |
| display_campaigns | advertiser_id.campaign_id | No pagination | ✅ |  ❌  |
| display_campaigns_metrics | date.advertiser_id.campaign_id | No pagination | ✅ |  ✅  |
| display_line_items | advertiser_id.campaign_id.line_item_id | No pagination | ✅ |  ❌  |
| display_line_items_metrics | date.advertiser_id.campaign_id.line_item_id | No pagination | ✅ |  ✅  |
| display_creatives | advertiser_id.campaign_id.line_item_id | No pagination | ✅ |  ❌  |
| product_advertisers | advertiser_id | No pagination | ✅ |  ❌  |
| product_campaigns | advertiser_id.campaign_id | DefaultPaginator | ✅ |  ❌  |
| product_campaigns_metrics | date.advertiser_id.campaign_id | DefaultPaginator | ✅ |  ✅  |
| product_items | advertiser_id.campaign_id.item_id | DefaultPaginator | ✅ |  ❌  |
| product_items_metrics | date.advertiser_id.campaign_id.item_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.19 | 2025-12-09 | [70785](https://github.com/airbytehq/airbyte/pull/70785) | Update dependencies |
| 0.0.18 | 2025-11-25 | [70094](https://github.com/airbytehq/airbyte/pull/70094) | Update dependencies |
| 0.0.17 | 2025-11-18 | [69576](https://github.com/airbytehq/airbyte/pull/69576) | Update dependencies |
| 0.0.16 | 2025-10-29 | [69068](https://github.com/airbytehq/airbyte/pull/69068) | Update dependencies |
| 0.0.15 | 2025-10-21 | [68437](https://github.com/airbytehq/airbyte/pull/68437) | Update dependencies |
| 0.0.14 | 2025-10-14 | [67833](https://github.com/airbytehq/airbyte/pull/67833) | Update dependencies |
| 0.0.13 | 2025-10-07 | [67378](https://github.com/airbytehq/airbyte/pull/67378) | Update dependencies |
| 0.0.12 | 2025-09-30 | [66343](https://github.com/airbytehq/airbyte/pull/66343) | Update dependencies |
| 0.0.11 | 2025-09-09 | [65839](https://github.com/airbytehq/airbyte/pull/65839) | Update dependencies |
| 0.0.10 | 2025-08-23 | [65192](https://github.com/airbytehq/airbyte/pull/65192) | Update dependencies |
| 0.0.9 | 2025-08-16 | [64977](https://github.com/airbytehq/airbyte/pull/64977) | Update dependencies |
| 0.0.8 | 2025-08-02 | [64270](https://github.com/airbytehq/airbyte/pull/64270) | Update dependencies |
| 0.0.7 | 2025-07-26 | [63897](https://github.com/airbytehq/airbyte/pull/63897) | Update dependencies |
| 0.0.6 | 2025-07-19 | [63442](https://github.com/airbytehq/airbyte/pull/63442) | Update dependencies |
| 0.0.5 | 2025-07-12 | [63257](https://github.com/airbytehq/airbyte/pull/63257) | Update dependencies |
| 0.0.4 | 2025-07-05 | [62576](https://github.com/airbytehq/airbyte/pull/62576) | Update dependencies |
| 0.0.3 | 2025-06-28 | [62401](https://github.com/airbytehq/airbyte/pull/62401) | Update dependencies |
| 0.0.2 | 2025-06-21 | [61136](https://github.com/airbytehq/airbyte/pull/61136) | Update dependencies |
| 0.0.1 | 2025-05-26 | | Initial release by [@joacoc2020](https://github.com/joacoc2020) via Connector Builder |

</details>
