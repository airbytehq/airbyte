# Fillout

The Airbyte connector for Fillout.com enables seamless data synchronization between Fillout forms and various target destinations. This connector allows you to extract form submissions and related data from Fillout and transfer it to your chosen data warehouse, analytics platform, or other destinations. With this integration, you can automate workflows, perform data analysis, and centralize data management for improved insights and reporting.

## Configuration

| Input        | Type     | Description                                                                             | Default Value |
| ------------ | -------- | --------------------------------------------------------------------------------------- | ------------- |
| `api_key`    | `string` | API Key. API key to use. Find it in the Developer settings tab of your Fillout account. |               |
| `start_date` | `string` | Start date.                                                                             |               |

## Streams

| Stream Name   | Primary Key  | Pagination       | Supports Full Sync | Supports Incremental |
| ------------- | ------------ | ---------------- | ------------------ | -------------------- |
| forms         | formId       | DefaultPaginator | ✅                 | ❌                   |
| form_metadata | id           | DefaultPaginator | ✅                 | ❌                   |
| submissions   | submissionId | DefaultPaginator | ✅                 | ✅                   |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request | Subject                                                                             |
| ------- | ---------- | ------------ | ----------------------------------------------------------------------------------- |
| 0.2.5 | 2025-01-11 | [51112](https://github.com/airbytehq/airbyte/pull/51112) | Update dependencies |
| 0.2.4 | 2024-12-28 | [50515](https://github.com/airbytehq/airbyte/pull/50515) | Update dependencies |
| 0.2.3 | 2024-12-21 | [50068](https://github.com/airbytehq/airbyte/pull/50068) | Update dependencies |
| 0.2.2 | 2024-12-14 | [49530](https://github.com/airbytehq/airbyte/pull/49530) | Update dependencies |
| 0.2.1 | 2024-12-12 | [49189](https://github.com/airbytehq/airbyte/pull/49189) | Update dependencies |
| 0.2.0   | 2024-11-14 |              | Add `formId` to `submissions` stream                                                |
| 0.0.1   | 2024-10-28 |              | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
