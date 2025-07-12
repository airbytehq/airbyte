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
| 0.0.12 | 2025-07-12 | [63160](https://github.com/airbytehq/airbyte/pull/63160) | Update dependencies |
| 0.0.11 | 2025-07-05 | [62752](https://github.com/airbytehq/airbyte/pull/62752) | Update dependencies |
| 0.0.10 | 2025-06-28 | [62228](https://github.com/airbytehq/airbyte/pull/62228) | Update dependencies |
| 0.0.9 | 2025-06-21 | [61755](https://github.com/airbytehq/airbyte/pull/61755) | Update dependencies |
| 0.0.8 | 2025-06-15 | [61254](https://github.com/airbytehq/airbyte/pull/61254) | Update dependencies |
| 0.0.7 | 2025-05-24 | [60740](https://github.com/airbytehq/airbyte/pull/60740) | Update dependencies |
| 0.0.6 | 2025-05-10 | [59975](https://github.com/airbytehq/airbyte/pull/59975) | Update dependencies |
| 0.0.5 | 2025-05-04 | [59528](https://github.com/airbytehq/airbyte/pull/59528) | Update dependencies |
| 0.0.4 | 2025-04-26 | [58959](https://github.com/airbytehq/airbyte/pull/58959) | Update dependencies |
| 0.0.3 | 2025-04-19 | [58562](https://github.com/airbytehq/airbyte/pull/58562) | Update dependencies |
| 0.0.2 | 2025-04-12 | [58020](https://github.com/airbytehq/airbyte/pull/58020) | Update dependencies |
| 0.0.1 | 2025-04-05 | [57406](https://github.com/airbytehq/airbyte/pull/57406) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
