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
| 0.0.42 | 2025-12-09 | [70731](https://github.com/airbytehq/airbyte/pull/70731) | Update dependencies |
| 0.0.41 | 2025-11-25 | [70190](https://github.com/airbytehq/airbyte/pull/70190) | Update dependencies |
| 0.0.40 | 2025-11-18 | [69700](https://github.com/airbytehq/airbyte/pull/69700) | Update dependencies |
| 0.0.39 | 2025-10-29 | [68949](https://github.com/airbytehq/airbyte/pull/68949) | Update dependencies |
| 0.0.38 | 2025-10-21 | [68387](https://github.com/airbytehq/airbyte/pull/68387) | Update dependencies |
| 0.0.37 | 2025-10-14 | [67968](https://github.com/airbytehq/airbyte/pull/67968) | Update dependencies |
| 0.0.36 | 2025-10-07 | [67331](https://github.com/airbytehq/airbyte/pull/67331) | Update dependencies |
| 0.0.35 | 2025-09-30 | [66448](https://github.com/airbytehq/airbyte/pull/66448) | Update dependencies |
| 0.0.34 | 2025-09-09 | [65727](https://github.com/airbytehq/airbyte/pull/65727) | Update dependencies |
| 0.0.33 | 2025-08-23 | [65408](https://github.com/airbytehq/airbyte/pull/65408) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64855](https://github.com/airbytehq/airbyte/pull/64855) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64393](https://github.com/airbytehq/airbyte/pull/64393) | Update dependencies |
| 0.0.30 | 2025-07-26 | [64050](https://github.com/airbytehq/airbyte/pull/64050) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63641](https://github.com/airbytehq/airbyte/pull/63641) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63235](https://github.com/airbytehq/airbyte/pull/63235) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62687](https://github.com/airbytehq/airbyte/pull/62687) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62204](https://github.com/airbytehq/airbyte/pull/62204) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61744](https://github.com/airbytehq/airbyte/pull/61744) | Update dependencies |
| 0.0.24 | 2025-06-15 | [61195](https://github.com/airbytehq/airbyte/pull/61195) | Update dependencies |
| 0.0.23 | 2025-05-24 | [59950](https://github.com/airbytehq/airbyte/pull/59950) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59544](https://github.com/airbytehq/airbyte/pull/59544) | Update dependencies |
| 0.0.21 | 2025-04-26 | [58960](https://github.com/airbytehq/airbyte/pull/58960) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58538](https://github.com/airbytehq/airbyte/pull/58538) | Update dependencies |
| 0.0.19 | 2025-04-12 | [58024](https://github.com/airbytehq/airbyte/pull/58024) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57418](https://github.com/airbytehq/airbyte/pull/57418) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56827](https://github.com/airbytehq/airbyte/pull/56827) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56322](https://github.com/airbytehq/airbyte/pull/56322) | Update dependencies |
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
