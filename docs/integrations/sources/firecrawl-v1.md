# Firecrawl v1
scrape, crawl, batch scrape

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `formats` | `array` | formats. all format options are:  String formats:  &quot;markdown&quot; (default) &quot;html&quot; &quot;rawHtml&quot; (no modifications) &quot;links&quot; &quot;summary&quot; &quot;images&quot; Object formats:  JSON: { &quot;type&quot;: &quot;json&quot;, &quot;prompt&quot;: &quot;...&quot;, &quot;schema&quot;: {...} } Screenshot: { &quot;type&quot;: &quot;screenshot&quot;, &quot;fullPage&quot;: true, &quot;quality&quot;: 80, &quot;viewport&quot;: {...} } Change tracking: { &quot;type&quot;: &quot;changeTracking&quot;, &quot;modes&quot;: [...], &quot;prompt&quot;: &quot;...&quot;, &quot;schema&quot;: {...}, &quot;tag&quot;: &quot;...&quot; } (requires markdown) |  |
| `batch_urls` | `array` | batch urls. List of URLs to scrape for Batch Scrape |  |
| `target_url` | `string` | target_url.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| scrape |  | No pagination | ✅ |  ❌  |
| crawl |  | No pagination | ✅ |  ❌  |
| batch scrape |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2025-11-15 | | Initial release by [@yoelferd](https://github.com/yoelferd) via Connector Builder |

</details>
