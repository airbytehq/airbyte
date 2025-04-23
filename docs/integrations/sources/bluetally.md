# Bluetally
Connector for fetching asset and employee data from Bluetelly

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key to authenticate with the BlueTally API. You can generate it by navigating to your account settings, selecting &#39;API Keys&#39;, and clicking &#39;Create API Key&#39;. |  |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| assets | id | DefaultPaginator | ✅ |  ✅  |
| employees | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2025-04-19 | [57644](https://github.com/airbytehq/airbyte/pull/57644) | Update dependencies |
| 0.0.1 | 2025-04-08 | | Initial release by [@wennergr](https://github.com/wennergr) via Connector Builder |

</details>
