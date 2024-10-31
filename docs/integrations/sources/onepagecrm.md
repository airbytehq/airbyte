# Onepagecrm
Onepagecrm is a CRM solution for small busineeses.
Using this stream we can extarct data from various streams such as contacts , deals , pipelines and meetings
Docs : https://developer.onepagecrm.com/api/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter the user ID of your API app |  |
| `password` | `string` | Password. Enter your API Key of your API app |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts |  | DefaultPaginator | ✅ |  ❌  |
| users |  | DefaultPaginator | ✅ |  ❌  |
| bootstrap |  | DefaultPaginator | ✅ |  ❌  |
| companies |  | DefaultPaginator | ✅ |  ❌  |
| actions |  | DefaultPaginator | ✅ |  ❌  |
| action_stream |  | DefaultPaginator | ✅ |  ❌  |
| team_stream |  | DefaultPaginator | ✅ |  ❌  |
| deals |  | DefaultPaginator | ✅ |  ❌  |
| notes |  | DefaultPaginator | ✅ |  ❌  |
| relationship_types |  | DefaultPaginator | ✅ |  ❌  |
| pipelines |  | DefaultPaginator | ✅ |  ❌  |
| statuses |  | DefaultPaginator | ✅ |  ❌  |
| lead_sources | id | DefaultPaginator | ✅ |  ❌  |
| filters |  | DefaultPaginator | ✅ |  ❌  |
| predefined_actions |  | DefaultPaginator | ✅ |  ❌  |
| predefined_items | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields |  | DefaultPaginator | ✅ |  ❌  |
| calls |  | DefaultPaginator | ✅ |  ❌  |
| meetings |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
