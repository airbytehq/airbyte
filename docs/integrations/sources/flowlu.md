# Flowlu
Flowlu connector enables seamless data integration between Flowlu, a project management and CRM platform, and various destinations supported by Airbyte. With this connector, users can automate the flow of project, finance, and CRM data into their preferred analytics or storage solutions for enhanced data analysis and reporting. This integration streamlines data syncing, reducing manual data transfer efforts and enhancing productivity.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. The API key to use for authentication |  |
| `company` | `string` | Sub Domain information for the Company.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields | id | DefaultPaginator | ✅ |  ❌  |
| agile_workflows | id | DefaultPaginator | ✅ |  ❌  |
| st_projects_users |  | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| account | id | DefaultPaginator | ✅ |  ❌  |
| agile_epics | id | DefaultPaginator | ✅ |  ❌  |
| loss_reason | id | DefaultPaginator | ✅ |  ❌  |
| pipeline |  | DefaultPaginator | ✅ |  ❌  |
| lead | id | DefaultPaginator | ✅ |  ❌  |
| emails | id | DefaultPaginator | ✅ |  ❌  |
| invoice | id | DefaultPaginator | ✅ |  ❌  |
| customer_payment | id | DefaultPaginator | ✅ |  ❌  |
| bank_account | id | DefaultPaginator | ✅ |  ❌  |
| agile_stages | id | DefaultPaginator | ✅ |  ❌  |
| agile_sprints | id | DefaultPaginator | ✅ |  ❌  |
| agile_issues | id | DefaultPaginator | ✅ |  ❌  |
| task_lists | id | DefaultPaginator | ✅ |  ❌  |
| lists | id | DefaultPaginator | ✅ |  ❌  |
| calendar | id | DefaultPaginator | ✅ |  ❌  |
| agile_issue_relation_types | id | DefaultPaginator | ✅ |  ❌  |
| agile_issue_relation_names | id | DefaultPaginator | ✅ |  ❌  |
| agile_issue_type | id | DefaultPaginator | ✅ |  ❌  |
| agile_categories | id | DefaultPaginator | ✅ |  ❌  |
| custom_fields_field_sets | id | DefaultPaginator | ✅ |  ❌  |
| product_list | id | DefaultPaginator | ✅ |  ❌  |
| product_categories | id | DefaultPaginator | ✅ |  ❌  |
| product_price_list | id | DefaultPaginator | ✅ |  ❌  |
| product_manufacturer | id | DefaultPaginator | ✅ |  ❌  |
| timesheet | id | DefaultPaginator | ✅ |  ❌  |
| estimates | id | DefaultPaginator | ✅ |  ❌  |
| transactions | id | DefaultPaginator | ✅ |  ❌  |
| invoice_items | id | DefaultPaginator | ✅ |  ❌  |
| invoice_contacts | id | DefaultPaginator | ✅ |  ❌  |
| project_observers | id | DefaultPaginator | ✅ |  ❌  |
| task_workflows | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-11 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
