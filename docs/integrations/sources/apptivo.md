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
| 0.0.22 | 2025-05-17 | [59839](https://github.com/airbytehq/airbyte/pull/59839) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59336](https://github.com/airbytehq/airbyte/pull/59336) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58738](https://github.com/airbytehq/airbyte/pull/58738) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58278](https://github.com/airbytehq/airbyte/pull/58278) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57660](https://github.com/airbytehq/airbyte/pull/57660) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57178](https://github.com/airbytehq/airbyte/pull/57178) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56567](https://github.com/airbytehq/airbyte/pull/56567) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56086](https://github.com/airbytehq/airbyte/pull/56086) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55356](https://github.com/airbytehq/airbyte/pull/55356) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54903](https://github.com/airbytehq/airbyte/pull/54903) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54225](https://github.com/airbytehq/airbyte/pull/54225) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53902](https://github.com/airbytehq/airbyte/pull/53902) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53401](https://github.com/airbytehq/airbyte/pull/53401) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52887](https://github.com/airbytehq/airbyte/pull/52887) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52184](https://github.com/airbytehq/airbyte/pull/52184) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51755](https://github.com/airbytehq/airbyte/pull/51755) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51228](https://github.com/airbytehq/airbyte/pull/51228) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50496](https://github.com/airbytehq/airbyte/pull/50496) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50193](https://github.com/airbytehq/airbyte/pull/50193) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49544](https://github.com/airbytehq/airbyte/pull/49544) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49004](https://github.com/airbytehq/airbyte/pull/49004) | Update dependencies |
| 0.0.1 | 2024-11-09 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
