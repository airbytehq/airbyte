# Web Scrapper
[Web Scrapper](https://webscraper.io/documentation/web-scraper-cloud/api) connector enables data synchronization from Web Scrapper source to various data destination. It gives information about sitemaps, users, scraping jobs etc.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | API Token. API token to use. Find it at https://cloud.webscraper.io/api |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| sitemap_list | id | DefaultPaginator | ✅ |  ❌  |
| sitemap_detail | id | DefaultPaginator | ✅ |  ❌  |
| users |  | No pagination | ✅ |  ❌  |
| scraping_jobs | id | DefaultPaginator | ✅ |  ❌  |
| scraping_job_data_quality |  | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.1 | 2024-10-29 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
