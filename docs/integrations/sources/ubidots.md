# Ubidots
The Ubidots Connector facilitates easy integration with the Ubidots IoT platform, enabling users to fetch, sync, and analyze real-time sensor data. This connector helps streamline IoT workflows by connecting Ubidots with other tools for seamless data processing and insights.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use for authentication. Obtain it from your Ubidots account. |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| devices | id | DefaultPaginator | ✅ |  ❌  |
| events | id | DefaultPaginator | ✅ |  ❌  |
| dashboards | id | DefaultPaginator | ✅ |  ❌  |
| variables | id | DefaultPaginator | ✅ |  ❌  |
| device_groups | id | DefaultPaginator | ✅ |  ❌  |
| device_types | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.6 | 2024-12-28 | [50806](https://github.com/airbytehq/airbyte/pull/50806) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50334](https://github.com/airbytehq/airbyte/pull/50334) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49758](https://github.com/airbytehq/airbyte/pull/49758) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49388](https://github.com/airbytehq/airbyte/pull/49388) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49127](https://github.com/airbytehq/airbyte/pull/49127) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-10-24 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
