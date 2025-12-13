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
| 0.0.43 | 2025-12-09 | [70725](https://github.com/airbytehq/airbyte/pull/70725) | Update dependencies |
| 0.0.42 | 2025-11-25 | [70169](https://github.com/airbytehq/airbyte/pull/70169) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69654](https://github.com/airbytehq/airbyte/pull/69654) | Update dependencies |
| 0.0.40 | 2025-10-29 | [68849](https://github.com/airbytehq/airbyte/pull/68849) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68390](https://github.com/airbytehq/airbyte/pull/68390) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67959](https://github.com/airbytehq/airbyte/pull/67959) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67503](https://github.com/airbytehq/airbyte/pull/67503) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66952](https://github.com/airbytehq/airbyte/pull/66952) | Update dependencies |
| 0.0.35 | 2025-09-09 | [65739](https://github.com/airbytehq/airbyte/pull/65739) | Update dependencies |
| 0.0.34 | 2025-08-23 | [65398](https://github.com/airbytehq/airbyte/pull/65398) | Update dependencies |
| 0.0.33 | 2025-08-09 | [64844](https://github.com/airbytehq/airbyte/pull/64844) | Update dependencies |
| 0.0.32 | 2025-08-02 | [64312](https://github.com/airbytehq/airbyte/pull/64312) | Update dependencies |
| 0.0.31 | 2025-07-26 | [64051](https://github.com/airbytehq/airbyte/pull/64051) | Update dependencies |
| 0.0.30 | 2025-07-20 | [63670](https://github.com/airbytehq/airbyte/pull/63670) | Update dependencies |
| 0.0.29 | 2025-07-12 | [63194](https://github.com/airbytehq/airbyte/pull/63194) | Update dependencies |
| 0.0.28 | 2025-07-05 | [62753](https://github.com/airbytehq/airbyte/pull/62753) | Update dependencies |
| 0.0.27 | 2025-06-28 | [62202](https://github.com/airbytehq/airbyte/pull/62202) | Update dependencies |
| 0.0.26 | 2025-06-21 | [61772](https://github.com/airbytehq/airbyte/pull/61772) | Update dependencies |
| 0.0.25 | 2025-06-15 | [61179](https://github.com/airbytehq/airbyte/pull/61179) | Update dependencies |
| 0.0.24 | 2025-05-24 | [60766](https://github.com/airbytehq/airbyte/pull/60766) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60017](https://github.com/airbytehq/airbyte/pull/60017) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59567](https://github.com/airbytehq/airbyte/pull/59567) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58929](https://github.com/airbytehq/airbyte/pull/58929) | Update dependencies |
| 0.0.20 | 2025-04-20 | [58573](https://github.com/airbytehq/airbyte/pull/58573) | Update dependencies |
| 0.0.19 | 2025-04-12 | [58019](https://github.com/airbytehq/airbyte/pull/58019) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57481](https://github.com/airbytehq/airbyte/pull/57481) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56808](https://github.com/airbytehq/airbyte/pull/56808) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56245](https://github.com/airbytehq/airbyte/pull/56245) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55639](https://github.com/airbytehq/airbyte/pull/55639) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55106](https://github.com/airbytehq/airbyte/pull/55106) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54530](https://github.com/airbytehq/airbyte/pull/54530) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54106](https://github.com/airbytehq/airbyte/pull/54106) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53579](https://github.com/airbytehq/airbyte/pull/53579) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53060](https://github.com/airbytehq/airbyte/pull/53060) | Update dependencies |
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
