# AgileCRM
The [Agile CRM](https://agilecrm.com/) Airbyte Connector allows you to sync and transfer data seamlessly from Agile CRM into your preferred data warehouse or analytics tool. With this connector, you can automate data extraction for various Agile CRM entities, such as contacts, companies, deals, and tasks, enabling easy integration and analysis of your CRM data in real-time. Ideal for businesses looking to streamline data workflows and enhance data accessibility.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `email` | `string` | Email Address. Your Agile CRM account email address. This is used as the username for authentication. |  |
| `domain` | `string` | Domain. The specific subdomain for your Agile CRM account |  |
| `api_key` | `string` | API Key. API key to use. Find it at Admin Settings -&gt; API &amp; Analytics -&gt; API Key in your Agile CRM account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| contacts | id | DefaultPaginator | ✅ |  ❌  |
| companies | id | DefaultPaginator | ✅ |  ❌  |
| deals | id | DefaultPaginator | ✅ |  ❌  |
| notes | id | No pagination | ✅ |  ❌  |
| tasks | id | No pagination | ✅ |  ❌  |
| milestone | id | No pagination | ✅ |  ❌  |
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| documents | id | No pagination | ✅ |  ❌  |
| ticket_filters | id | No pagination | ✅ |  ❌  |
| tickets |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-11-08 | | Initial release by [@parthiv11](https://github.com/parthiv11) via Connector Builder |

</details>
