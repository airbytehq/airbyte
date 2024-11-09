# Fillout
The Airbyte connector for Fillout.com enables seamless data synchronization between Fillout forms and various target destinations. This connector allows you to extract form submissions and related data from Fillout and transfer it to your chosen data warehouse, analytics platform, or other destinations. With this integration, you can automate workflows, perform data analysis, and centralize data management for improved insights and reporting.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use. Find it in the Developer settings tab of your Fillout account. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| forms | formId | DefaultPaginator | ✅ |  ❌  |
| form_metadata | id | DefaultPaginator | ✅ |  ❌  |
| submissions | submissionId | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-28 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
