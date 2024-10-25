# Concord
This is the setup for the Concord source which ingests data from the concord API.

Concord turns contract data into financial insights. Sign, store and search unlimited contracts https://www.concord.app/

In order to use this source, you must first create a concord account and log in. Then navigate to Automations -&gt; Integrations -&gt; Concord API -&gt; Generate New Key to obtain your API key.

The API is accessible from two environments, sandbox and production. You can learn more about the API here https://api.doc.concordnow.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `env` | `string` | Environment. The environment from where you want to access the API. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| agreements | uid | DefaultPaginator | ✅ |  ❌  |
| user_organizations | id | No pagination | ✅ |  ❌  |
| organization | id | No pagination | ✅ |  ❌  |
| folders | id | No pagination | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | No pagination | ✅ |  ❌  |
| organization_members | user_id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-25 | | Initial release by [@marcosmarxm](https://github.com/marcosmarxm) via Connector Builder |

</details>
