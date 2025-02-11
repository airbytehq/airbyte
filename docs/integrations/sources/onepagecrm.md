# Onepagecrm
Onepagecrm is a CRM solution for small busineeses.
Using this stream we can extarct data from various streams such as contacts , deals , pipelines and meetings
[API Documentation](https://developer.onepagecrm.com/api/)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter the user ID of your API app |  |
| `password` | `string` | Password. Enter your API Key of your API app |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| bootstrap | user_id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| actions | id | DefaultPaginator | ✅ |  ❌  |
| action_stream |  | DefaultPaginator | ✅ |  ❌  |
| team_stream |  | DefaultPaginator | ✅ |  ❌  |
| deals | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | DefaultPaginator | ✅ |  ❌  |
| relationship_types | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | id | DefaultPaginator | ✅ |  ❌  |
| statuses | id | DefaultPaginator | ✅ |  ❌  |
| lead_sources | id | DefaultPaginator | ✅ |  ❌  |
| filters | id | DefaultPaginator | ✅ |  ❌  |
| predefined_actions | id | DefaultPaginator | ✅ |  ❌  |
| predefined_items | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| calls | id | DefaultPaginator | ✅ |  ❌  |
| meetings | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.10 | 2025-02-08 | [53460](https://github.com/airbytehq/airbyte/pull/53460) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52476](https://github.com/airbytehq/airbyte/pull/52476) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51895](https://github.com/airbytehq/airbyte/pull/51895) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51341](https://github.com/airbytehq/airbyte/pull/51341) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50745](https://github.com/airbytehq/airbyte/pull/50745) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50231](https://github.com/airbytehq/airbyte/pull/50231) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49729](https://github.com/airbytehq/airbyte/pull/49729) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49330](https://github.com/airbytehq/airbyte/pull/49330) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49072](https://github.com/airbytehq/airbyte/pull/49072) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
