# Zoho Campaign
The Zoho Campaigns connector enables seamless integration of mailing lists, campaign data, and subscriber management into your data workflows. Easily extract subscriber information, campaign reports, and list details to sync with your data warehouse or BI tools, automating marketing insights and analytics

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id_2` | `string` | Client ID.  |  |
| `client_secret_2` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `domain` | `string` | Domain.  |  |
| `campaign_recipients_data_action` | `string` | Campaign Recipients Data Action.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | campaign_key | No pagination | ✅ |  ❌  |
| subscribers | contact_email | No pagination | ✅ |  ❌  |
| lists | listkey | No pagination | ✅ |  ❌  |
| campaignrecipients | contactid | No pagination | ✅ |  ❌  |
| campaignreports | campaign_name | No pagination | ✅ |  ❌  |
| recentcampaigns | campaign_key | No pagination | ✅ |  ❌  |
| recentsentcampaigns | campaign_key | No pagination | ✅ |  ❌  |
| mailinglists | listunino | No pagination | ✅ |  ❌  |
| totalcontacts |  | No pagination | ✅ |  ❌  |
| topics | topicId | No pagination | ✅ |  ❌  |
| campaigndetails | campaign_name | No pagination | ✅ |  ❌  |
| alltags |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-14 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
