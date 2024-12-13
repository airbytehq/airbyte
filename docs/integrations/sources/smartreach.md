# Smartreach
Smartreach is a sales engagement platform.
Using this connector we extract data from two streams : campaigns and prospects.
Docs : https://smartreach.io/api_docs#smartreach-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `teamid` | `number` | TeamID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | id | No pagination | ✅ |  ❌  |
| prospects |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2024-12-12 | [49406](https://github.com/airbytehq/airbyte/pull/49406) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49113](https://github.com/airbytehq/airbyte/pull/49113) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-01 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
