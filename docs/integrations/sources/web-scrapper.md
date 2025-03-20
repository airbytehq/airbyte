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
| 0.0.15 | 2025-03-08 | [55614](https://github.com/airbytehq/airbyte/pull/55614) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55086](https://github.com/airbytehq/airbyte/pull/55086) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54465](https://github.com/airbytehq/airbyte/pull/54465) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54038](https://github.com/airbytehq/airbyte/pull/54038) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53556](https://github.com/airbytehq/airbyte/pull/53556) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53102](https://github.com/airbytehq/airbyte/pull/53102) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52396](https://github.com/airbytehq/airbyte/pull/52396) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51429](https://github.com/airbytehq/airbyte/pull/51429) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50754](https://github.com/airbytehq/airbyte/pull/50754) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50370](https://github.com/airbytehq/airbyte/pull/50370) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49778](https://github.com/airbytehq/airbyte/pull/49778) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49393](https://github.com/airbytehq/airbyte/pull/49393) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49115](https://github.com/airbytehq/airbyte/pull/49115) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-11-04 | [48269](https://github.com/airbytehq/airbyte/pull/48269) | Update dependencies |
| 0.0.1 | 2024-10-29 | | Initial release by [@bishalbera](https://github.com/bishalbera) via Connector Builder |

</details>
