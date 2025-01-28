# Uservoice
Airbyte connector for UserVoice.com allows users to efficiently extract data from the UserVoice  and integrate it with various data destinations. This connector can sync data such as user feedback, suggestions, comments, tickets, and support metrics, providing a streamlined way to analyze and act on customer feedback. It supports incremental data syncs, ensuring that new or updated data is captured without duplication. The connector is designed for easy setup, enabling seamless integration with UserVoice's API to ensure your customer insights are always up to date.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `subdomain` | `string` | Subdomain.  |  |
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forums | id | DefaultPaginator | ✅ |  ✅  |
| external_accounts | id | DefaultPaginator | ✅ |  ✅  |
| external_users | id | DefaultPaginator | ✅ |  ✅  |
| features | id | DefaultPaginator | ✅ |  ✅  |
| feedback_records | id | DefaultPaginator | ✅ |  ✅  |
| suggestions | id | DefaultPaginator | ✅ |  ✅  |
| attachments | id | DefaultPaginator | ✅ |  ✅  |
| categories | id | DefaultPaginator | ✅ |  ✅  |
| comments | id | DefaultPaginator | ✅ |  ✅  |
| custom_fields | id | DefaultPaginator | ✅ |  ✅  |
| feature_statuses | id | DefaultPaginator | ✅ |  ✅  |
| forum_invitations | id | DefaultPaginator | ✅ |  ✅  |
| importance_responses | id | DefaultPaginator | ✅ |  ❌  |
| importance_scores | id | DefaultPaginator | ✅ |  ❌  |
| internal_status_updates | id | DefaultPaginator | ✅ |  ❌  |
| internal_flags | id | DefaultPaginator | ✅ |  ✅  |
| internal_statuses | id | DefaultPaginator | ✅ |  ✅  |
| labels | id | DefaultPaginator | ✅ |  ✅  |
| permissions | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ✅  |
| product_areas | id | DefaultPaginator | ✅ |  ✅  |
| segmented_values | id | DefaultPaginator | ✅ |  ✅  |
| segments | id | DefaultPaginator | ✅ |  ✅  |
| service_hook_logs | id | DefaultPaginator | ✅ |  ❌  |
| status_updates | id | DefaultPaginator | ✅ |  ✅  |
| statuses | id | DefaultPaginator | ✅ |  ✅  |
| supporter_messages |  | DefaultPaginator | ✅ |  ✅  |
| suggested_merges | id | DefaultPaginator | ✅ |  ✅  |
| suggestion_activity_entries | id | DefaultPaginator | ✅ |  ❌  |
| supporters | id | DefaultPaginator | ✅ |  ✅  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| translatable_strings |  | No pagination | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.9 | 2025-01-25 | [52448](https://github.com/airbytehq/airbyte/pull/52448) | Update dependencies |
| 0.0.8 | 2025-01-18 | [52021](https://github.com/airbytehq/airbyte/pull/52021) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51434](https://github.com/airbytehq/airbyte/pull/51434) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50773](https://github.com/airbytehq/airbyte/pull/50773) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50318](https://github.com/airbytehq/airbyte/pull/50318) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49397](https://github.com/airbytehq/airbyte/pull/49397) | Update dependencies |
| 0.0.3 | 2024-11-04 | [48290](https://github.com/airbytehq/airbyte/pull/48290) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47500](https://github.com/airbytehq/airbyte/pull/47500) | Update dependencies |
| 0.0.1 | 2024-10-16 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
