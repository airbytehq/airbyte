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
| 0.0.23 | 2025-06-15 | [61189](https://github.com/airbytehq/airbyte/pull/61189) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60759](https://github.com/airbytehq/airbyte/pull/60759) | Update dependencies |
| 0.0.21 | 2025-05-10 | [60001](https://github.com/airbytehq/airbyte/pull/60001) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59539](https://github.com/airbytehq/airbyte/pull/59539) | Update dependencies |
| 0.0.19 | 2025-04-26 | [58955](https://github.com/airbytehq/airbyte/pull/58955) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58572](https://github.com/airbytehq/airbyte/pull/58572) | Update dependencies |
| 0.0.17 | 2025-04-13 | [58039](https://github.com/airbytehq/airbyte/pull/58039) | Update dependencies |
| 0.0.16 | 2025-04-05 | [57395](https://github.com/airbytehq/airbyte/pull/57395) | Update dependencies |
| 0.0.15 | 2025-03-29 | [56823](https://github.com/airbytehq/airbyte/pull/56823) | Update dependencies |
| 0.0.14 | 2025-03-22 | [56336](https://github.com/airbytehq/airbyte/pull/56336) | Update dependencies |
| 0.0.13 | 2025-03-09 | [55660](https://github.com/airbytehq/airbyte/pull/55660) | Update dependencies |
| 0.0.12 | 2025-03-01 | [55166](https://github.com/airbytehq/airbyte/pull/55166) | Update dependencies |
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
