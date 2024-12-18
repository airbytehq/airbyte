# Zoho Campaign
The Zoho Campaigns connector enables seamless integration of mailing lists, campaign data, and subscriber management into your data workflows. Easily extract subscriber information, campaign reports, and list details to sync with your data warehouse or BI tools, automating marketing insights and analytics

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id_2` | `string` | Client ID.  |  |
| `client_secret_2` | `string` | Client secret.  |  |
| `client_refresh_token` | `string` | Refresh token.  |  |
| `domain` | `string` | Domain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| recent_campaigns | campaign_key | DefaultPaginator | ✅ |  ❌  |
| campaign_recipients | contactid, sent_time | DefaultPaginator | ✅ |  ❌  |
| campaign_details | campaign_name | No pagination | ✅ |  ❌  |
| campaign_reports | campaign_name | No pagination | ✅ |  ❌  |
| recent_sent_campaigns | campaign_key | DefaultPaginator | ✅ |  ❌  |
| mailing_lists | listunino | DefaultPaginator | ✅ |  ❌  |
| subscribers | contact_email |  DefaultPaginator | ✅ |  ❌  |
| lists | listkey | No pagination | ✅ |  ❌  |
| total_contacts |  | No pagination | ✅ |  ❌  |
| topics | topicId | No pagination | ✅ |  ❌  |
| all_tags |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2024-12-14 | [49452](https://github.com/airbytehq/airbyte/pull/49452) | Update dependencies |
| 0.0.1 | 2024-10-14 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
