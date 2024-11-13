# Apptivo
Apptivo connector  seamless data integration between Apptivo and various data warehouses or databases, automating data transfer for analytics, reporting, and insights. This connector allows businesses to synchronize Apptivo CRM data, such as contacts, deals, and activities, with other systems to streamline workflows and improve data accessibility across platforms.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it in your Apptivo account under Business Settings -&gt; API Access. |  |
| `access_key` | `string` | Access Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| customers | customerId | DefaultPaginator | ✅ |  ❌  |
| contacts | contactId | DefaultPaginator | ✅ |  ❌  |
| cases |  | No pagination | ✅ |  ❌  |
| leads | id | DefaultPaginator | ✅ |  ❌  |
| opportunities | opportunityId | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-09 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
