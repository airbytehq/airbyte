# Thinkific Courses
Getting Course information from thinkific

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `X-Auth-Subdomain` | `string` | subdomain.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Courses |  | DefaultPaginator | ✅ |  ❌  |
| Chapters |  | No pagination | ✅ |  ❌  |
| Contents |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-02-20 | | Initial release by [@gueroverde](https://github.com/gueroverde) via Connector Builder |

</details>
