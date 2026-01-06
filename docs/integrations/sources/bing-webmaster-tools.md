# Bing Webmaster Tools
The Bing Webmaster Tools source allows you to sync SEO and technical site performance data from Microsoft Bing. It retrieves critical metrics such as crawl statistics, keyword query performance, and daily rank/traffic summaries to help you analyze your website&#39;s search engine visibility

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `site_url` | `string` | Site URL.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| query_stats |  | No pagination | ✅ |  ❌  |
| traffic_stats |  | No pagination | ✅ |  ❌  |
| crawl_stats |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-01-06 | | Initial release by [@zykyan](https://github.com/zykyan) via Connector Builder |

</details>
