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
| 0.0.1 | 2024-10-31 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
