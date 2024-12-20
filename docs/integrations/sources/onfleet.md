# Onfleet
This is the Onfleet connector that ingests data from the Onfleet API.

Onfleet is the world&#39;s advanced logistics software that delights customers, scale operations, and boost efficiency https://onfleet.com/

In order to use this source you must first create an account on Onfleet. Once logged in, you can find the can create an API keys through the settings menu in the dashboard, by going into the API section.

You can find more information about the API here https://docs.onfleet.com/reference/setup-tutorial

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. API key to use for authenticating requests. You can create and manage your API keys in the API section of the Onfleet dashboard. |  |
| `password` | `string` | Placeholder Password. Placeholder for basic HTTP auth password - should be set to empty string | x |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| workers | id | No pagination | ✅ |  ❌  |
| administrators | id | No pagination | ✅ |  ❌  |
| teams | id | No pagination | ✅ |  ❌  |
| hubs | id | No pagination | ✅ |  ❌  |
| tasks | id | DefaultPaginator | ✅ |  ❌  |
| containers | id | No pagination | ✅ |  ❌  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.4 | 2024-12-14 | [49712](https://github.com/airbytehq/airbyte/pull/49712) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49336](https://github.com/airbytehq/airbyte/pull/49336) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49051](https://github.com/airbytehq/airbyte/pull/49051) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-27 | | Initial release by [@aazam-gh](https://github.com/aazam-gh) via Connector Builder |

</details>
