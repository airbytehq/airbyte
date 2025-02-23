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
| 0.0.13 | 2025-02-22 | [54480](https://github.com/airbytehq/airbyte/pull/54480) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54098](https://github.com/airbytehq/airbyte/pull/54098) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53577](https://github.com/airbytehq/airbyte/pull/53577) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53082](https://github.com/airbytehq/airbyte/pull/53082) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52394](https://github.com/airbytehq/airbyte/pull/52394) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51995](https://github.com/airbytehq/airbyte/pull/51995) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51379](https://github.com/airbytehq/airbyte/pull/51379) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50814](https://github.com/airbytehq/airbyte/pull/50814) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50351](https://github.com/airbytehq/airbyte/pull/50351) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49749](https://github.com/airbytehq/airbyte/pull/49749) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49406](https://github.com/airbytehq/airbyte/pull/49406) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49113](https://github.com/airbytehq/airbyte/pull/49113) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-01 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
