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
| 0.2.13 | 2025-03-08 | [55317](https://github.com/airbytehq/airbyte/pull/55317) | Update dependencies |
| 0.2.12 | 2025-03-01 | [54943](https://github.com/airbytehq/airbyte/pull/54943) | Update dependencies |
| 0.2.11 | 2025-02-22 | [54388](https://github.com/airbytehq/airbyte/pull/54388) | Update dependencies |
| 0.2.10 | 2025-02-15 | [53771](https://github.com/airbytehq/airbyte/pull/53771) | Update dependencies |
| 0.2.9 | 2025-02-08 | [53327](https://github.com/airbytehq/airbyte/pull/53327) | Update dependencies |
| 0.2.8 | 2025-02-01 | [52800](https://github.com/airbytehq/airbyte/pull/52800) | Update dependencies |
| 0.2.7 | 2025-01-25 | [52352](https://github.com/airbytehq/airbyte/pull/52352) | Update dependencies |
| 0.2.6 | 2025-01-18 | [51689](https://github.com/airbytehq/airbyte/pull/51689) | Update dependencies |
| 0.2.5 | 2025-01-11 | [51112](https://github.com/airbytehq/airbyte/pull/51112) | Update dependencies |
| 0.2.4 | 2024-12-28 | [50515](https://github.com/airbytehq/airbyte/pull/50515) | Update dependencies |
| 0.2.3 | 2024-12-21 | [50068](https://github.com/airbytehq/airbyte/pull/50068) | Update dependencies |
| 0.2.2 | 2024-12-14 | [49530](https://github.com/airbytehq/airbyte/pull/49530) | Update dependencies |
| 0.2.1 | 2024-12-12 | [49189](https://github.com/airbytehq/airbyte/pull/49189) | Update dependencies |
| 0.2.0   | 2024-11-14 |              | Add `formId` to `submissions` stream                                                |
| 0.0.1   | 2024-10-28 |              | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
