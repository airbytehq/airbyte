# NoCRM
[NoCRM](https://nocrm.io) connector enables seamless data integration between NoCRM.io, a lead management tool, and other platforms or data warehouses. It allows for the automated extraction and synchronization of lead data, activities, and contact details from NoCRM.io into analytics  systems, supporting data-driven decisions and streamlined workflows. 

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Generate it from the admin section of your noCRM.io account. |  |
| `subdomain` | `string` | Subdomain. The subdomain specific to your noCRM.io account, e.g., &#39;yourcompany&#39; in &#39;yourcompany.nocrm.io&#39;. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| steps | id | DefaultPaginator | ✅ |  ❌  |
| pipelines | id | DefaultPaginator | ✅ |  ❌  |
| clients_folders | id | DefaultPaginator | ✅ |  ❌  |
| categories | id | DefaultPaginator | ✅ |  ❌  |
| predefined_tags | id | DefaultPaginator | ✅ |  ❌  |
| fields | id | DefaultPaginator | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| follow_ups | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| teams | id | DefaultPaginator | ✅ |  ❌  |
| webhooks | id | DefaultPaginator | ✅ |  ❌  |
| webhook_events | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-31 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
