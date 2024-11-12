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
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
