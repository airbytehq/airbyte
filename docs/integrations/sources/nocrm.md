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
| steps | id | No pagination | ✅ |  ❌  |
| pipelines | id | No pagination | ✅ |  ❌  |
| clients_folders | id | No pagination | ✅ |  ❌  |
| categories | id | No pagination | ✅ |  ❌  |
| predefined_tags | id | No pagination | ✅ |  ❌  |
| fields | id | No pagination | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| follow_ups | id | No pagination | ✅ |  ❌  |
| users | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| webhooks | id | No pagination | ✅ |  ❌  |
| webhook_events | id | No pagination | ✅ |  ❌  |
| activities | id | No pagination | ✅ |  ❌  |
| prospecting_lists | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2024-12-14 | [49635](https://github.com/airbytehq/airbyte/pull/49635) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49252](https://github.com/airbytehq/airbyte/pull/49252) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48944](https://github.com/airbytehq/airbyte/pull/48944) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
