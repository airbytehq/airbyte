# AdRoll
Docs : https://developers.adroll.com/apis

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `Authorization` | `string` | Person Access Token (Authorization).  |  |
| `client_id` | `string` | Client ID.  |  |
| `client_secret` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `oauth_access_token` | `string` | Access token. The current access token. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `oauth_token_expiry_date` | `string` | Token expiry date. The date the current access token expires in. This field might be overridden by the connector based on the token refresh endpoint response. |  |
| `advertisable` | `string` | Advertisable EID .  |  |
| `adgroup_eid` | `string` | AdGroup EID.  |  |
| `campaign_eid` | `string` | Campaign EID.  |  |
| `strategy_eid` | `string` | Strategy EID.  |  |
| `pixel_eid` | `string` | Pixel EID.  |  |
| `eid_of_asset` | `string` | EID of Asset.  |  |
| `eid_of_ad` | `string` | EID of Ad.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Assets by EID | eid | No pagination | ✅ |  ❌  |
| Segments | segment_id | No pagination | ✅ |  ❌  |
| AdGroup |  | No pagination | ✅ |  ❌  |
| Campaign |  | No pagination | ✅ |  ❌  |
| Strategy |  | No pagination | ✅ |  ❌  |
| All Startegies |  | No pagination | ✅ |  ❌  |
| Geo Target |  | No pagination | ✅ |  ❌  |
| Advertisable |  | No pagination | ✅ |  ❌  |
| Active Pixels for an Advertisable |  | No pagination | ✅ |  ❌  |
| Consent Banner Config for an Advertisable |  | No pagination | ✅ |  ❌  |
| Pixel | eid | No pagination | ✅ |  ❌  |
| Segments for a Pixel | eid | No pagination | ✅ |  ❌  |
| All Campaigns | eid | No pagination | ✅ |  ❌  |
| All AdGroups | eid | No pagination | ✅ |  ❌  |
| All Ads | eid | No pagination | ✅ |  ❌  |
| All Ads by AdGroup | eid | No pagination | ✅ |  ❌  |
| All AdGroups by Campaign |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-06 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
