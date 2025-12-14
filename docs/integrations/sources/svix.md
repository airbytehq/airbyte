# Svix
Website: https://dashboard.svix.com/
API Reference: https://api.svix.com/docs#section/Introduction

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key or access token |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| applications | id | DefaultPaginator | ✅ |  ✅  |
| event_types | uuid | DefaultPaginator | ✅ |  ✅  |
| tokens | id | DefaultPaginator | ✅ |  ✅  |
| endpoints | id | DefaultPaginator | ✅ |  ✅  |
| integrations | id | DefaultPaginator | ✅ |  ✅  |
| ingest_source | id | DefaultPaginator | ✅ |  ✅  |
| ingest_source_endpoint | id | DefaultPaginator | ✅ |  ✅  |
| webhook_endpoint | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.22 | 2025-12-09 | [70637](https://github.com/airbytehq/airbyte/pull/70637) | Update dependencies |
| 0.0.21 | 2025-11-25 | [70063](https://github.com/airbytehq/airbyte/pull/70063) | Update dependencies |
| 0.0.20 | 2025-11-18 | [69527](https://github.com/airbytehq/airbyte/pull/69527) | Update dependencies |
| 0.0.19 | 2025-10-29 | [68993](https://github.com/airbytehq/airbyte/pull/68993) | Update dependencies |
| 0.0.18 | 2025-10-21 | [68525](https://github.com/airbytehq/airbyte/pull/68525) | Update dependencies |
| 0.0.17 | 2025-10-14 | [67884](https://github.com/airbytehq/airbyte/pull/67884) | Update dependencies |
| 0.0.16 | 2025-10-07 | [67455](https://github.com/airbytehq/airbyte/pull/67455) | Update dependencies |
| 0.0.15 | 2025-09-30 | [66881](https://github.com/airbytehq/airbyte/pull/66881) | Update dependencies |
| 0.0.14 | 2025-09-23 | [66362](https://github.com/airbytehq/airbyte/pull/66362) | Update dependencies |
| 0.0.13 | 2025-09-09 | [66122](https://github.com/airbytehq/airbyte/pull/66122) | Update dependencies |
| 0.0.12 | 2025-08-23 | [64999](https://github.com/airbytehq/airbyte/pull/64999) | Update dependencies |
| 0.0.11 | 2025-08-02 | [64458](https://github.com/airbytehq/airbyte/pull/64458) | Update dependencies |
| 0.0.10 | 2025-07-19 | [63609](https://github.com/airbytehq/airbyte/pull/63609) | Update dependencies |
| 0.0.9 | 2025-07-05 | [62680](https://github.com/airbytehq/airbyte/pull/62680) | Update dependencies |
| 0.0.8 | 2025-06-28 | [61305](https://github.com/airbytehq/airbyte/pull/61305) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60462](https://github.com/airbytehq/airbyte/pull/60462) | Update dependencies |
| 0.0.6 | 2025-05-10 | [60193](https://github.com/airbytehq/airbyte/pull/60193) | Update dependencies |
| 0.0.5 | 2025-05-04 | [59592](https://github.com/airbytehq/airbyte/pull/59592) | Update dependencies |
| 0.0.4 | 2025-04-27 | [59026](https://github.com/airbytehq/airbyte/pull/59026) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58429](https://github.com/airbytehq/airbyte/pull/58429) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57997](https://github.com/airbytehq/airbyte/pull/57997) | Update dependencies |
| 0.0.1 | 2025-04-06 | [57495](https://github.com/airbytehq/airbyte/pull/57495) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
