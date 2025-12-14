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
| 0.0.25 | 2025-12-09 | [70694](https://github.com/airbytehq/airbyte/pull/70694) | Update dependencies |
| 0.0.24 | 2025-11-25 | [69895](https://github.com/airbytehq/airbyte/pull/69895) | Update dependencies |
| 0.0.23 | 2025-11-18 | [69399](https://github.com/airbytehq/airbyte/pull/69399) | Update dependencies |
| 0.0.22 | 2025-10-29 | [69008](https://github.com/airbytehq/airbyte/pull/69008) | Update dependencies |
| 0.0.21 | 2025-10-21 | [68320](https://github.com/airbytehq/airbyte/pull/68320) | Update dependencies |
| 0.0.20 | 2025-10-14 | [68010](https://github.com/airbytehq/airbyte/pull/68010) | Update dependencies |
| 0.0.19 | 2025-10-07 | [67255](https://github.com/airbytehq/airbyte/pull/67255) | Update dependencies |
| 0.0.18 | 2025-09-30 | [66300](https://github.com/airbytehq/airbyte/pull/66300) | Update dependencies |
| 0.0.17 | 2025-09-09 | [66101](https://github.com/airbytehq/airbyte/pull/66101) | Update dependencies |
| 0.0.16 | 2025-08-23 | [65390](https://github.com/airbytehq/airbyte/pull/65390) | Update dependencies |
| 0.0.15 | 2025-08-09 | [64588](https://github.com/airbytehq/airbyte/pull/64588) | Update dependencies |
| 0.0.14 | 2025-08-02 | [64191](https://github.com/airbytehq/airbyte/pull/64191) | Update dependencies |
| 0.0.13 | 2025-07-26 | [63888](https://github.com/airbytehq/airbyte/pull/63888) | Update dependencies |
| 0.0.12 | 2025-07-19 | [63505](https://github.com/airbytehq/airbyte/pull/63505) | Update dependencies |
| 0.0.11 | 2025-07-12 | [63148](https://github.com/airbytehq/airbyte/pull/63148) | Update dependencies |
| 0.0.10 | 2025-07-05 | [62610](https://github.com/airbytehq/airbyte/pull/62610) | Update dependencies |
| 0.0.9 | 2025-06-28 | [62188](https://github.com/airbytehq/airbyte/pull/62188) | Update dependencies |
| 0.0.8 | 2025-06-21 | [61793](https://github.com/airbytehq/airbyte/pull/61793) | Update dependencies |
| 0.0.7 | 2025-06-14 | [61265](https://github.com/airbytehq/airbyte/pull/61265) | Update dependencies |
| 0.0.6 | 2025-05-24 | [60352](https://github.com/airbytehq/airbyte/pull/60352) | Update dependencies |
| 0.0.5 | 2025-05-10 | [59970](https://github.com/airbytehq/airbyte/pull/59970) | Update dependencies |
| 0.0.4 | 2025-05-03 | [59440](https://github.com/airbytehq/airbyte/pull/59440) | Update dependencies |
| 0.0.3 | 2025-04-26 | [58318](https://github.com/airbytehq/airbyte/pull/58318) | Update dependencies |
| 0.0.2 | 2025-04-12 | [57763](https://github.com/airbytehq/airbyte/pull/57763) | Update dependencies |
| 0.0.1 | 2025-04-07 | [57503](https://github.com/airbytehq/airbyte/pull/57503) | Initial release by [@btkcodedev](https://github.com/btkcodedev) via Connector Builder |

</details>
