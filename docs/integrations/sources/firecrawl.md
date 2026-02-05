# Firecrawl
FireCrawl- Turn websites into LLM-ready data

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `url` | `string` | Target URL. URL to scrape or crawl (required for scrape/crawl/map streams) |  |
| `urls` | `array` | Target URLs (Batch Scrape). List of URLs for batch_scrape_stream. If set, batch_scrape_stream uses this; otherwise uses [url] when url is set. |  |
| `proxy` | `string` | Proxy Type. basic (fast), enhanced (anti-bot), auto (retry with enhanced if needed) | auto |
| `mobile` | `boolean` | Mobile Emulation. Emulate mobile device (e.g. for mobile screenshots) | false |
| `api_key` | `string` | API Key. Firecrawl API key for authentication |  |
| `api_url` | `string` | API URL. Firecrawl API base URL (default: https://api.firecrawl.dev) | https://api.firecrawl.dev |
| `formats` | `array` | Output Formats. Content formats to extract (markdown, html, changeTracking, etc.) | [markdown] |
| `parsers` | `array` | parsers.  | [pdf] |
| `sitemap` | `string` | Crawl Sitemap Mode. skip, include, or only (crawl). include = sitemap + discovery. | include |
| `block_ads` | `boolean` | Block Ads. Enable ad-blocking and cookie popup blocking | true |
| `agent_urls` | `array` | Agent URLs. Optional URLs to constrain agent to | [] |
| `max_age_ms` | `number` | Cache Max Age (ms). Use cached page if younger than this (ms). Default 172800000 (2 days). Speeds up scrapes. | 172800000 |
| `search_tbs` | `string` | Search Time Range. Time filter: qdr:h (hour), qdr:d (day), qdr:w (week), qdr:m (month), qdr:y (year) |  |
| `agent_model` | `string` | Agent Model. spark-1-mini (cheaper) or spark-1-pro (higher accuracy) | spark-1-mini |
| `map_sitemap` | `string` | Map Sitemap Mode. skip, include, or only for URL discovery | include |
| `webhook_url` | `string` | Webhook URL. Optional webhook URL to receive crawl events (started, page, completed) |  |
| `agent_job_id` | `string` | Agent Job ID. Job ID for agent_status_stream (from agent_stream response) |  |
| `agent_prompt` | `string` | Agent Prompt. Prompt for agent_stream (agentic extraction). Required for agent_stream. |  |
| `crawl_job_id` | `string` | Crawl Job ID. Job ID for crawl_status_stream and crawl_errors_stream (from crawl_stream response) |  |
| `exclude_tags` | `array` | Exclude Tags. HTML tags to exclude from extraction | [nav, footer, script, style] |
| `extract_urls` | `array` | Extract URLs. URLs to extract structured data from (required for extract_stream). Glob format supported. |  |
| `include_tags` | `array` | Include Tags. HTML tags to include in extraction | [article, main] |
| `search_query` | `string` | Search Query. Query for search endpoint (required for search_stream) |  |
| `exclude_paths` | `array` | Exclude Paths (Crawl). URL path regex patterns to exclude (e.g. [&quot;blog/.*&quot;]) | [] |
| `include_paths` | `array` | Include Paths (Crawl). URL path regex patterns to include only (e.g. [&quot;docs/.*&quot;]) | [] |
| `search_filter` | `string` | Search Filter. Optional search filter for map endpoint (relevance ordering) |  |
| `extract_job_id` | `string` | Extract Job ID. Completed extract job ID from POST /v2/extract (required for extract_results_stream) |  |
| `extract_prompt` | `string` | Extract Prompt. Prompt to guide LLM extraction (for extract_stream) |  |
| `search_country` | `string` | Search Country. ISO country code for search (e.g. US, DE, FR) | US |
| `search_sources` | `array` | Search Sources. Search sources: web, images, news | [web] |
| `store_in_cache` | `boolean` | Store in Cache. Store scraped pages in Firecrawl cache | true |
| `webhook_events` | `array` | Webhook Events. Events to subscribe to (started, page, completed) | [completed] |
| `search_location` | `string` | Search Location. Geo-target for search (e.g. Germany, San Francisco California United States) |  |
| `map_ignore_cache` | `boolean` | Map Ignore Cache. Bypass sitemap cache for fresh URLs | false |
| `batch_scrape_urls` | `array` | Batch Scrape URLs (async). URLs for batch_scrape_job_stream (POST /v2/batch/scrape). Falls back to urls if not set. Required for batch scraping operations. |  |
| `crawl_preview_url` | `string` | Crawl Preview URL. URL for crawl_params_preview_stream (natural language to params) |  |
| `only_main_content` | `boolean` | Only Main Content. Extract only main content, excluding navigation and footer (default: true) | true |
| `search_categories` | `array` | Search Categories. Filter by category: github, research, pdf | [] |
| `search_timeout_ms` | `number` | Search Timeout (ms). Timeout for search request |  |
| `include_subdomains` | `boolean` | Include Subdomains. Whether to include subdomains when crawling (default: false) | false |
| `batch_scrape_job_id` | `string` | Batch Scrape Job ID. Job ID for batch_scrape_status_stream and batch_scrape_errors_stream (from batch_scrape_job_stream response) |  |
| `crawl_delay_seconds` | `number` | Crawl Delay (seconds). Delay in seconds between scrapes (rate limiting). Firecrawl API requires &gt; 0; minimum 1. |  |
| `crawl_entire_domain` | `boolean` | Crawl Entire Domain. Follow sibling/parent URLs, not just child paths | false |
| `allow_external_links` | `boolean` | Allow External Links (Crawl). Follow links to external websites | false |
| `crawl_preview_prompt` | `string` | Crawl Preview Prompt. Natural language prompt for crawl_params_preview_stream |  |
| `extract_show_sources` | `boolean` | Extract Show Sources. Include sources used for extraction in response | false |
| `enable_change_tracking` | `boolean` | Enable Change Tracking. Enable change tracking to detect website updates (default: false) | false |
| `extract_ignore_sitemap` | `boolean` | Extract Ignore Sitemap. Ignore sitemap.xml during website scanning | false |
| `ignore_query_parameters` | `boolean` | Ignore Query Parameters (Crawl). Do not re-scrape same path with different query params | false |
| `extract_enable_web_search` | `boolean` | Extract Enable Web Search. Use web search to find additional data during extraction | false |
| `extract_include_subdomains` | `boolean` | Extract Include Subdomains. Scan subdomains of provided URLs | true |
| `include_images_in_markdown` | `boolean` | Include Images in Markdown. Default false = no images (excluded). If true, markdown includes base64-encoded images; if false, images are removed and replaced with placeholders (alt text remains). | false |
| `search_ignore_invalid_urls` | `boolean` | Search Ignore Invalid URLs. Exclude URLs invalid for other Firecrawl endpoints | false |
| `extract_ignore_invalid_urls` | `boolean` | Extract Ignore Invalid URLs. Skip invalid URLs and return them in invalidURLs instead of failing | true |
| `map_ignore_query_parameters` | `boolean` | Map Ignore Query Parameters. Do not return URLs with query parameters | true |
| `agent_strict_constrain_to_urls` | `boolean` | Agent Strict Constrain to URLs. If true, agent only visits provided URLs | false |
| `batch_scrape_ignore_invalid_urls` | `boolean` | Batch Scrape Ignore Invalid URLs. Skip invalid URLs in async batch | true |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| scrape_stream |  | No pagination | ✅ |  ❌  |
| batch_scrape_stream |  | No pagination | ✅ |  ❌  |
| crawl_stream |  | No pagination | ✅ |  ❌  |
| search_stream |  | No pagination | ✅ |  ❌  |
| map_stream |  | No pagination | ✅ |  ❌  |
| extract_stream | id | No pagination | ✅ |  ❌  |
| extract_results_stream | id | No pagination | ✅ |  ❌  |
| batch_scrape_job_stream | id | No pagination | ✅ |  ❌  |
| batch_scrape_status_stream |  | No pagination | ✅ |  ❌  |
| batch_scrape_errors_stream |  | No pagination | ✅ |  ❌  |
| crawl_status_stream |  | No pagination | ✅ |  ❌  |
| crawl_errors_stream |  | No pagination | ✅ |  ❌  |
| active_crawls_stream | id | No pagination | ✅ |  ❌  |
| crawl_params_preview_stream |  | No pagination | ✅ |  ❌  |
| agent_stream | id | No pagination | ✅ |  ❌  |
| agent_status_stream |  | No pagination | ✅ |  ❌  |
| credit_usage_stream |  | No pagination | ✅ |  ❌  |
| credit_usage_historical_stream | startDate.endDate | No pagination | ✅ |  ❌  |
| token_usage_stream |  | No pagination | ✅ |  ❌  |
| token_usage_historical_stream | startDate.endDate | No pagination | ✅ |  ❌  |
| queue_status_stream |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2026-02-05 | | Initial release by [@ashhadahsan](https://github.com/ashhadahsan) via Connector Builder |

</details>
