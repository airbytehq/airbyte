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
| 0.0.11 | 2025-02-22 | [54406](https://github.com/airbytehq/airbyte/pull/54406) | Update dependencies |
| 0.0.10 | 2025-02-15 | [53353](https://github.com/airbytehq/airbyte/pull/53353) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52811](https://github.com/airbytehq/airbyte/pull/52811) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52361](https://github.com/airbytehq/airbyte/pull/52361) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51623](https://github.com/airbytehq/airbyte/pull/51623) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51066](https://github.com/airbytehq/airbyte/pull/51066) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50538](https://github.com/airbytehq/airbyte/pull/50538) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50034](https://github.com/airbytehq/airbyte/pull/50034) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49518](https://github.com/airbytehq/airbyte/pull/49518) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48921](https://github.com/airbytehq/airbyte/pull/48921) | Update dependencies |
| 0.0.1 | 2024-11-11 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
