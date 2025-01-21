# Sendowl
Sendowl is an All-in-One Digital Commerce Platform.
Using this connector we can extract data from products , packages , orders , discounts and subscriptions streams.
[API Docs](https://dashboard.sendowl.com/developers/api/introduction)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `username` | `string` | Username. Enter you API Key |  |
| `password` | `string` | Password. Enter your API secret |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| products | id | DefaultPaginator | ✅ |  ❌  |
| packages | id | DefaultPaginator | ✅ |  ❌  |
| orders | id | DefaultPaginator | ✅ |  ✅  |
| subscriptions | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.8 | 2025-01-18 | [51915](https://github.com/airbytehq/airbyte/pull/51915) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51363](https://github.com/airbytehq/airbyte/pull/51363) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50711](https://github.com/airbytehq/airbyte/pull/50711) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50248](https://github.com/airbytehq/airbyte/pull/50248) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49683](https://github.com/airbytehq/airbyte/pull/49683) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49338](https://github.com/airbytehq/airbyte/pull/49338) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49054](https://github.com/airbytehq/airbyte/pull/49054) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-09 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
