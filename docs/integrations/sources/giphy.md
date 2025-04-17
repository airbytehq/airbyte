# Giphy
Website: https://giphy.com/
API Reference: https://developers.giphy.com/docs/api/endpoint/#trending

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key. Your GIPHY API Key. You can create and find your API key in the GIPHY Developer Dashboard at https://developers.giphy.com/dashboard/. |  |
| `start_date` | `string` | Start date.  |  |
| `query` | `string` | Query for search endpoints. A query for search endpoint | foo |
| `query_for_gif` | `string` | Query for gif search endpoint. Query for gif search endpoint | foo |
| `query_for_stickers` | `string` | Query for stickers search endpoint. Query for stickers search endpoint | foo |
| `query_for_clips` | `string` | Query for clips search endpoint. Query for clips search endpoint | foo |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| categories | name | DefaultPaginator | ✅ |  ❌  |
| emoji | id | DefaultPaginator | ✅ |  ✅  |
| autocomplete_tags | name | DefaultPaginator | ✅ |  ❌  |
| channel_search | id | DefaultPaginator | ✅ |  ❌  |
| gifs_search | id | DefaultPaginator | ✅ |  ✅  |
| stickers_search | uuid | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.2 | 2025-04-12 | [57763](https://github.com/airbytehq/airbyte/pull/57763) | Update dependencies |
| 0.0.1 | 2025-04-07 | [57503](https://github.com/airbytehq/airbyte/pull/57503) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
