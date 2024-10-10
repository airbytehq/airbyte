# Bunny, Inc.
Synchronizes Bunny accounts

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `subdomain` | `string` | Subdomain. The subdomain specific to your Bunny account or service. |  |
| `api_key_2` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| accounts | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-07 | | Initial release by [@tbpeders](https://github.com/tbpeders) via Connector Builder |

</details>
