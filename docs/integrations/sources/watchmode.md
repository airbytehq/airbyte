# Watchmode
Website: https://watchmode.com/
API Reference: https://api.watchmode.com/docs

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your API key for authenticating with the Watchmode API. You can request a free API key at https://api.watchmode.com/requestApiKey/. |  |
| `search_val` | `string` | Search Value. The name value for search stream | Terminator |
| `start_date` | `string` | Start date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| sources | id | DefaultPaginator | ✅ |  ❌  |
| regions | uuid | DefaultPaginator | ✅ |  ❌  |
| networks | id | No pagination | ✅ |  ❌  |
| genres | id | DefaultPaginator | ✅ |  ❌  |
| search | id | DefaultPaginator | ✅ |  ❌  |
| autocomplete_search | id | DefaultPaginator | ✅ |  ❌  |
| titles | id | DefaultPaginator | ✅ |  ❌  |
| releases | id | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.3 | 2025-04-19 | [58562](https://github.com/airbytehq/airbyte/pull/58562) | Update dependencies |
| 0.0.2 | 2025-04-12 | [58020](https://github.com/airbytehq/airbyte/pull/58020) | Update dependencies |
| 0.0.1 | 2025-04-05 | [57406](https://github.com/airbytehq/airbyte/pull/57406) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
