# SpotlerCRM
The Airbyte connector for [Spotler CRM](https://spotler.com/) enables seamless data integration, allowing users to sync customer data from Spotler CRM into their data warehouses or other tools. It supports automated data extraction from Spotler CRM, making it easier to analyze and leverage customer insights across multiple platforms. With this connector, businesses can efficiently streamline their customer relationship data and maintain up-to-date records for improved decision-making and marketing efforts.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `access_token` | `string` | Access Token. Access Token to authenticate API requests. Generate it by logging into your CRM system, navigating to Settings / Integrations / API V4, and clicking &#39;generate new key&#39;. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| opportunities | id | DefaultPaginator | ✅ |  ❌  |
| documents |  | DefaultPaginator | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
|  cases | id | DefaultPaginator | ✅ |  ❌  |
| activities | id | DefaultPaginator | ✅ |  ❌  |
| opportunity_histories | id | DefaultPaginator | ✅ |  ❌  |
| opportunity_lines | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.7 | 2025-01-25 | [52433](https://github.com/airbytehq/airbyte/pull/52433) | Update dependencies |
| 0.0.6 | 2025-01-18 | [51967](https://github.com/airbytehq/airbyte/pull/51967) | Update dependencies |
| 0.0.5 | 2025-01-11 | [51391](https://github.com/airbytehq/airbyte/pull/51391) | Update dependencies |
| 0.0.4 | 2024-12-28 | [50770](https://github.com/airbytehq/airbyte/pull/50770) | Update dependencies |
| 0.0.3 | 2024-12-21 | [50322](https://github.com/airbytehq/airbyte/pull/50322) | Update dependencies |
| 0.0.2 | 2024-12-14 | [49436](https://github.com/airbytehq/airbyte/pull/49436) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
