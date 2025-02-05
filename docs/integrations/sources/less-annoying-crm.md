# Less Annoying CRM
Less Annoying CRM connector  enables seamless data integration, allowing users to easily sync customer relationship management data into their data warehouses or analytics tools. This connector facilitates efficient tracking of customer information, interactions, and leads, helping businesses centralize CRM data for enhanced analysis and insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Manage and create your API keys on the Programmer API settings page at https://account.lessannoyingcrm.com/app/Settings/Api. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users |  | DefaultPaginator | ✅ |  ❌  |
| contacts | ContactId | DefaultPaginator | ✅ |  ❌  |
| tasks |  | DefaultPaginator | ✅ |  ✅  |
| pipeline_items | PipelineItemId | DefaultPaginator | ✅ |  ❌  |
| notes | NoteId | DefaultPaginator | ✅ |  ❌  |
| teams | TeamId | No pagination | ✅ |  ❌  |
| events | EventId | DefaultPaginator | ✅ |  ✅  |
| contact_events |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-02-01 | [52759](https://github.com/airbytehq/airbyte/pull/52759) | Update dependencies |
| 0.0.7 | 2025-01-25 | [52231](https://github.com/airbytehq/airbyte/pull/52231) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51826](https://github.com/airbytehq/airbyte/pull/51826) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51143](https://github.com/airbytehq/airbyte/pull/51143) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50665](https://github.com/airbytehq/airbyte/pull/50665) | Update dependencies |
| 0.0.3 | 2024-12-21 | [49606](https://github.com/airbytehq/airbyte/pull/49606) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49227](https://github.com/airbytehq/airbyte/pull/49227) | Update dependencies |
| 0.0.1 | 2024-10-31 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
