# Flowlu
Flowlu connector enables seamless data integration between Flowlu, a project management and CRM platform, and various destinations supported by Airbyte. With this connector, users can automate the flow of project, finance, and CRM data into their preferred analytics or storage solutions for enhanced data analysis and reporting. This integration streamlines data syncing, reducing manual data transfer efforts and enhancing productivity.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |
| `company` | `string` | company.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| fields | id | DefaultPaginator | ✅ |  ❌  |
| workflows | id | DefaultPaginator | ✅ |  ❌  |
| projects_users |  | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| account | id | DefaultPaginator | ✅ |  ❌  |
| epics | id | DefaultPaginator | ✅ |  ❌  |
| loss_reason | id | DefaultPaginator | ✅ |  ❌  |
| pipeline |  | DefaultPaginator | ✅ |  ❌  |
| lead | id | DefaultPaginator | ✅ |  ❌  |
| emails | id | DefaultPaginator | ✅ |  ❌  |
| invoice | id | DefaultPaginator | ✅ |  ❌  |
| customer_payment | id | DefaultPaginator | ✅ |  ❌  |
| bank_account | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-01 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
