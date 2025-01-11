# Concord
This is the setup for the Concord source which ingests data from the concord API.

Concord turns contract data into financial insights. Sign, store and search unlimited contracts https://www.concord.app/

In order to use this source, you must first create a concord account and log in. Then navigate to Automations -> Integrations -> Concord API -> Generate New Key to obtain your API key.

The API is accessible from two environments, sandbox and production. You can learn more about the API here https://api.doc.concordnow.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `environment` | `string` | enviornment. The environment from where you want to access the API https://api.doc.concordnow.com/#section/Environments. |  |


## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| agreements | uid | DefaultPaginator | ✅ |  ❌  |
| user_organizations | id | No pagination | ✅ |  ❌  |
| organization | id | No pagination | ✅ |  ❌  |
| folders | id | No pagination | ✅ |  ❌  |
| reports | id | DefaultPaginator | ✅ |  ❌  |
| tags | id | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-01-11 | [51131](https://github.com/airbytehq/airbyte/pull/51131) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50510](https://github.com/airbytehq/airbyte/pull/50510) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50057](https://github.com/airbytehq/airbyte/pull/50057) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49475](https://github.com/airbytehq/airbyte/pull/49475) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49160](https://github.com/airbytehq/airbyte/pull/49160) | Update dependencies |
| 0.0.3 | 2024-12-11 | [48913](https://github.com/airbytehq/airbyte/pull/48913) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-11-04 | [48215](https://github.com/airbytehq/airbyte/pull/48215) | Update dependencies |
| 0.0.1 | 2024-10-16 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
