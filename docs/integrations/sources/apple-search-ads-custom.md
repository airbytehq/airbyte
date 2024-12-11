# Apple Search Ads
Update api to v5

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `org_id` | `integer` | Org Id. The identifier of the organization that owns the campaign. Your Org Id is the same as your account in the Apple Search Ads UI. |  |
| `end_date` | `string` | End Date. Data is retrieved until that date (included) |  |
| `client_id` | `string` | Client Id. A user identifier for the token request. See &lt;a href=&quot;https://developer.apple.com/documentation/apple_search_ads/implementing_oauth_for_the_apple_search_ads_api&quot;&gt;here&lt;/a&gt; |  |
| `start_date` | `string` | Start Date. Start getting data from that date. |  |
| `client_secret` | `string` | Client Secret. A string that authenticates the user’s setup request. See &lt;a href=&quot;https://developer.apple.com/documentation/apple_search_ads/implementing_oauth_for_the_apple_search_ads_api&quot;&gt;here&lt;/a&gt; |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| adgroups | id | DefaultPaginator | ✅ |  ❌  |
| keywords | id | DefaultPaginator | ✅ |  ❌  |
| campaigns_report_daily | date.campaignId | No pagination | ✅ |  ✅  |
| adgroups_report_daily | date.adGroupId | No pagination | ✅ |  ✅  |
| keywords_report_daily | date.keywordId | No pagination | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-12-11 | | Initial release by [@canhhungit](https://github.com/canhhungit) via Connector Builder |

</details>
