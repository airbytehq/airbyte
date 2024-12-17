# PandaDoc
Airbyte connector for PandaDoc allows users to extract data from PandaDoc and integrate it into various data warehouses or databases. This connector functions as a source, pulling data such as documents, templates, and related metadata from PandaDoc.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it at https://app.pandadoc.com/a/#/settings/api-dashboard/configuration |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| documents | id | DefaultPaginator | ✅ |  ✅  |
| document_attachment | uuid | No pagination | ✅ |  ❌  |
| document_field | uuid | No pagination | ✅ |  ❌  |
| document_section | uuid | No pagination | ✅ |  ❌  |
| templates |  | DefaultPaginator | ✅ |  ❌  |
| forms | id | No pagination | ✅ |  ✅  |
| contacts | id | No pagination | ✅ |  ❌  |
| members | user_id | No pagination | ✅ |  ✅  |
| api_logs | id | DefaultPaginator | ✅ |  ❌  |
| document_folders | uuid | DefaultPaginator | ✅ |  ❌  |
| template_folders | uuid | No pagination | ✅ |  ❌  |
| workspaces | id | DefaultPaginator | ✅ |  ❌  |
| webhook_subscriptions | uuid | No pagination | ✅ |  ❌  |
| webhook_events | uuid | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2024-11-04 | [48210](https://github.com/airbytehq/airbyte/pull/48210) | Update dependencies |
| 0.0.2 | 2024-10-29 | [47911](https://github.com/airbytehq/airbyte/pull/47911) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
