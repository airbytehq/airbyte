# TwentyCRM
TwentyCRM with connection to people, companies and opportunities REST endpoints.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `domain` | `string` | domain.  |  |
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| people |  | DefaultPaginator | ✅ |  ❌  |
| companies |  | DefaultPaginator | ✅ |  ❌  |
| opportunities |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-03-21 | | Initial release by [@lucasagon](https://github.com/lucasagon) via Connector Builder |

</details>
