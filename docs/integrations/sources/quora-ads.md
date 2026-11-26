# Quora Ads
Documentation reference:
Visit https://www.quora.com/ads/api9169a6d6e9b42452d500a61717d87d15d5fa49ec5b53030741178130#section/Overview for API documentation

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | Client ID.  |  |
| `account_id` | `string` | Account ID.  |  |
| `start_date` | `string` | Start date.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `conversion_types` | `array` | Conversion types. Additional conversion types to return for the `conversions` and `conversionRate` fields. Quora returns `Generic` only by default, so any other type your account fires is silently absent until listed here. `Generic` is always included whether or not it appears in this list, and cannot be removed. Downstream models read it as a named key, so dropping it would null those columns rather than fail visibly. Listing it explicitly is harmless. | [Generic] |
| `attribution_windows` | `array` | Attribution windows. Windows used to attribute a conversion back to a click or view. Keep the streams&#39; `lookback_window` at least as long as the longest window selected here, or conversions attributed late are never re-fetched and the historical rows stay short. | [CLICK_28_DAY, VIEW_1_DAY] |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| account | date.accountId | DefaultPaginator | ✅ |  ✅  |
| campaign_summary | date.campaignId | DefaultPaginator | ✅ |  ✅  |
| adset_summary | date.adSetId | DefaultPaginator | ✅ |  ✅  |
| ad_summary | date.adId | DefaultPaginator | ✅ |  ✅  |
| accounts | accountId | No pagination | ✅ |  ❌  |
| lead_gen_forms | id | No pagination | ✅ |  ❌  |
| recent_leads | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-08-20 | | Initial release by [@nicolabiano](https://github.com/nicolabiano) via Connector Builder |

</details>
