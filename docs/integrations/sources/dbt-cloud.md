# dbt Cloud
This is used to connect to dbt Cloud with the V2 API

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key_2` | `string` | Service Token.  |  |
| `account_id` | `string` | Account ID.  |  |
| `access_url` | `string` | Access URL.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| runs | id | DefaultPaginator | ✅ |  ❌  |
| projects | id | DefaultPaginator | ✅ |  ❌  |
| repositories | id | DefaultPaginator | ✅ |  ❌  |
| users | id | DefaultPaginator | ✅ |  ❌  |
| environments | id | DefaultPaginator | ✅ |  ❌  |
| jobs | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-12-12 | | Initial release by [@VolubleRain1](https://github.com/VolubleRain1) via Connector Builder |

</details>
