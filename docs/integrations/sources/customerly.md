# Customerly
Connector for customerly.io

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| users | user_id.email | DefaultPaginator | ✅ |  ✅  |
| leads | crmhero_user_id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2025-03-22 | [55940](https://github.com/airbytehq/airbyte/pull/55940) | Update dependencies |
| 0.0.1 | 2025-03-18 | | Initial release by [@Shuky](https://github.com/Shuky) via Connector Builder |

</details>
