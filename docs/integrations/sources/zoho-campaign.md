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
| 0.0.11 | 2025-02-23 | [54628](https://github.com/airbytehq/airbyte/pull/54628) | Update dependencies |
| 0.0.10 | 2025-02-15 | [54116](https://github.com/airbytehq/airbyte/pull/54116) | Update dependencies |
| 0.0.9 | 2025-02-08 | [53593](https://github.com/airbytehq/airbyte/pull/53593) | Update dependencies |
| 0.0.8 | 2025-02-01 | [53115](https://github.com/airbytehq/airbyte/pull/53115) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52552](https://github.com/airbytehq/airbyte/pull/52552) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51938](https://github.com/airbytehq/airbyte/pull/51938) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51464](https://github.com/airbytehq/airbyte/pull/51464) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50830](https://github.com/airbytehq/airbyte/pull/50830) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50390](https://github.com/airbytehq/airbyte/pull/50390) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49452](https://github.com/airbytehq/airbyte/pull/49452) | Update dependencies |
| 0.0.1 | 2024-10-14 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
