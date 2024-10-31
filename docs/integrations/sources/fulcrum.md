# Fulcrum
Airbyte connector for Fulcrum would enable seamless data extraction from the Fulcrum platform, allowing users to sync survey and field data with their data warehouses or other applications. This connector would facilitate automated, scheduled transfers of structured data, improving analytics, reporting, and decision-making processes by integrating Fulcrum's powerful field data collection capabilities with a broader data ecosystem.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://web.fulcrumapp.com/settings/api |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forms | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| workflows |  | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |
| changesets | id | DefaultPaginator | ✅ |  ❌  |
| records | id | DefaultPaginator | ✅ |  ❌  |
| signatures | record_id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| layers | id | DefaultPaginator | ✅ |  ❌  |
| classification_sets | id | DefaultPaginator | ✅ |  ❌  |
| choice_lists | id | DefaultPaginator | ✅ |  ❌  |
| groups | id | DefaultPaginator | ✅ |  ❌  |
| memberships | id | DefaultPaginator | ✅ |  ❌  |
| roles | id | DefaultPaginator | ✅ |  ❌  |
| authorizations | id | DefaultPaginator | ✅ |  ❌  |
| photos | record_id | DefaultPaginator | ✅ |  ❌  |
| audio | record_id | DefaultPaginator | ✅ |  ❌  |
| videos | record_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
