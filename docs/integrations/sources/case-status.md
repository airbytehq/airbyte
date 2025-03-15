# Case Status
Source Connector for the Case Status app allowing the export of cases, messages, and files. 

https://www.casestatus.com/

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Prefix with &#39;ApiKey &#39; then insert your API Key |  |
| `base_url` | `string` | Base Url. Base URL | https://app.casestatus.com |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Messages |  | DefaultPaginator | ✅ |  ❌  |
| Cases |  | DefaultPaginator | ✅ |  ❌  |
| Firm Reporting |  | DefaultPaginator | ✅ |  ❌  |
| Files |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-03-05 | | Initial release by [@atritch](https://github.com/atritch) via Connector Builder |

</details>
