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
| 0.0.1 | 2024-10-24 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
