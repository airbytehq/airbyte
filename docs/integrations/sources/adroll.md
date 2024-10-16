# AdRoll
AdRoll is an ecommerce marketing platform that gives growing D2C brands the power to connect with customers wherever they are.
This connector allows you to extract data from various AdRoll APIs such as Advertisables , Ads , Campaigns , Strategies and many more
Docs : https://developers.adroll.com/apis

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `Authorization` | `string` | Person Access Token (Authorization).  |  |
| `client_id` | `string` | Client ID. The key ID of your app |  |
| `client_secret` | `string` | Client secret. The secret of your app |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Segments | segment_id | No pagination | ✅ |  ❌  |
| Campaign | campaign_eid | DefaultPaginator | ✅ |  ❌  |
| Strategy |  | No pagination | ✅ |  ❌  |
| Strategies | eid | DefaultPaginator | ✅ |  ❌  |
| Advertisable |  | No pagination | ✅ |  ❌  |
| Active Pixels for an Advertisable | eid | No pagination | ✅ |  ❌  |
| Consent Banner Config for an Advertisable |  | No pagination | ✅ |  ❌  |
| Pixel | eid | No pagination | ✅ |  ❌  |
| Segments for a Pixel | eid | No pagination | ✅ |  ❌  |
| Campaigns | eid | No pagination | ✅ |  ❌  |
| AdGroups by Advertisables | eid | No pagination | ✅ |  ❌  |
| Ads | eid | No pagination | ✅ |  ❌  |
| All Ads by AdGroup |  | No pagination | ✅ |  ❌  |
| AdGroups by Campaigns |  | No pagination | ✅ |  ❌  |
| Advertisables | eid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-16 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
