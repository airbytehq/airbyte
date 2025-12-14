# SimFin
Simfin provides financial data .
With this connector we can extract data from price data , financial statements and company info streams .
Docs https://simfin.readme.io/reference/getting-started-1

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Company Info  | id | No pagination | ✅ |  ❌  |
| Financial Statements |  | No pagination | ✅ |  ❌  |
| Price Data |  | No pagination | ✅ |  ❌  |
| companies |  | No pagination | ✅ |  ❌  |
| common_shares_outstanding |  | No pagination | ✅ |  ❌  |
| weighted_shares_outstanding |  | No pagination | ✅ |  ❌  |
| filings_by_company | filingIdentifier | No pagination | ✅ |  ❌  |
| filings_list | filingIdentifier | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.41 | 2025-12-09 | [70691](https://github.com/airbytehq/airbyte/pull/70691) | Update dependencies |
| 0.0.40 | 2025-11-25 | [70070](https://github.com/airbytehq/airbyte/pull/70070) | Update dependencies |
| 0.0.39 | 2025-11-18 | [69452](https://github.com/airbytehq/airbyte/pull/69452) | Update dependencies |
| 0.0.38 | 2025-10-29 | [68780](https://github.com/airbytehq/airbyte/pull/68780) | Update dependencies |
| 0.0.37 | 2025-10-21 | [68268](https://github.com/airbytehq/airbyte/pull/68268) | Update dependencies |
| 0.0.36 | 2025-10-14 | [67771](https://github.com/airbytehq/airbyte/pull/67771) | Update dependencies |
| 0.0.35 | 2025-10-07 | [67443](https://github.com/airbytehq/airbyte/pull/67443) | Update dependencies |
| 0.0.34 | 2025-09-30 | [66916](https://github.com/airbytehq/airbyte/pull/66916) | Update dependencies |
| 0.0.33 | 2025-09-24 | [66259](https://github.com/airbytehq/airbyte/pull/66259) | Update dependencies |
| 0.0.32 | 2025-09-09 | [66109](https://github.com/airbytehq/airbyte/pull/66109) | Update dependencies |
| 0.0.31 | 2025-08-23 | [65402](https://github.com/airbytehq/airbyte/pull/65402) | Update dependencies |
| 0.0.30 | 2025-08-09 | [64851](https://github.com/airbytehq/airbyte/pull/64851) | Update dependencies |
| 0.0.29 | 2025-08-02 | [64456](https://github.com/airbytehq/airbyte/pull/64456) | Update dependencies |
| 0.0.28 | 2025-07-26 | [63941](https://github.com/airbytehq/airbyte/pull/63941) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63614](https://github.com/airbytehq/airbyte/pull/63614) | Update dependencies |
| 0.0.26 | 2025-07-05 | [62721](https://github.com/airbytehq/airbyte/pull/62721) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62235](https://github.com/airbytehq/airbyte/pull/62235) | Update dependencies |
| 0.0.24 | 2025-06-21 | [61803](https://github.com/airbytehq/airbyte/pull/61803) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61614](https://github.com/airbytehq/airbyte/pull/61614) | Update dependencies |
| 0.0.22 | 2025-05-25 | [60523](https://github.com/airbytehq/airbyte/pull/60523) | Update dependencies |
| 0.0.21 | 2025-05-10 | [60103](https://github.com/airbytehq/airbyte/pull/60103) | Update dependencies |
| 0.0.20 | 2025-05-04 | [59596](https://github.com/airbytehq/airbyte/pull/59596) | Update dependencies |
| 0.0.19 | 2025-04-27 | [59006](https://github.com/airbytehq/airbyte/pull/59006) | Update dependencies |
| 0.0.18 | 2025-04-19 | [58386](https://github.com/airbytehq/airbyte/pull/58386) | Update dependencies |
| 0.0.17 | 2025-04-12 | [57970](https://github.com/airbytehq/airbyte/pull/57970) | Update dependencies |
| 0.0.16 | 2025-04-05 | [56324](https://github.com/airbytehq/airbyte/pull/56324) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55606](https://github.com/airbytehq/airbyte/pull/55606) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55099](https://github.com/airbytehq/airbyte/pull/55099) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54509](https://github.com/airbytehq/airbyte/pull/54509) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54074](https://github.com/airbytehq/airbyte/pull/54074) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53578](https://github.com/airbytehq/airbyte/pull/53578) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53084](https://github.com/airbytehq/airbyte/pull/53084) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52401](https://github.com/airbytehq/airbyte/pull/52401) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51949](https://github.com/airbytehq/airbyte/pull/51949) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51397](https://github.com/airbytehq/airbyte/pull/51397) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50776](https://github.com/airbytehq/airbyte/pull/50776) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50306](https://github.com/airbytehq/airbyte/pull/50306) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49790](https://github.com/airbytehq/airbyte/pull/49790) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49390](https://github.com/airbytehq/airbyte/pull/49390) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49118](https://github.com/airbytehq/airbyte/pull/49118) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
