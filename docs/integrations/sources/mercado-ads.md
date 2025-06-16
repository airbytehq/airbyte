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
| 0.0.1 | 2025-05-26 | | Initial release by [@joacoc2020](https://github.com/joacoc2020) via Connector Builder |

</details>
