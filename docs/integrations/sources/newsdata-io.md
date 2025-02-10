# NewsData.io
Connector for NewsData.io to get the latest news in pagination and the latest news from specific countries, categories and domains. You can also get the news sources from specific categories, countries and languages.

:::info
Historical News is only available for premium users of NewsData service.
:::

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date.  |  |
| `end_date` | `string` | End Date.  |  |
| `categories` | `string` | Categories to filter news.  |  |
| `countries` | `string` | Countries to filter news.  |  |
| `languages` | `string` | Language to filter news.  |  |
| `domains` | `string` | Specific domains to filter news  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| latest_news | `article_id` | DefaultPaginator | ✅ |  ❌  |
| historical_news | `article_id` | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.11 | 2025-02-08 | [53259](https://github.com/airbytehq/airbyte/pull/53259) | Update dependencies |
| 0.0.10 | 2025-02-01 | [52723](https://github.com/airbytehq/airbyte/pull/52723) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52262](https://github.com/airbytehq/airbyte/pull/52262) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51801](https://github.com/airbytehq/airbyte/pull/51801) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51173](https://github.com/airbytehq/airbyte/pull/51173) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50643](https://github.com/airbytehq/airbyte/pull/50643) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50097](https://github.com/airbytehq/airbyte/pull/50097) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49630](https://github.com/airbytehq/airbyte/pull/49630) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49259](https://github.com/airbytehq/airbyte/pull/49259) | Update dependencies |
| 0.0.2 | 2024-12-11 | [48999](https://github.com/airbytehq/airbyte/pull/48999) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@faria-karim-porna](https://github.com/faria-karim-porna) via Connector Builder |

</details>
