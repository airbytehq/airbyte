# Marketstack
Marketstack provides data from 72 global stock exchanges.
Using this connector we can extract Historical Data , Splits and Dividends data !

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `start_date` | `string` | Start Date.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| Exchanges | mic | DefaultPaginator | ✅ |  ❌  |
| Tickers | symbol | DefaultPaginator | ✅ |  ❌  |
| Historical Data |  | DefaultPaginator | ✅ |  ✅  |
| Splits |  | DefaultPaginator | ✅ |  ❌  |
| Dividends |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date              | Pull Request | Subject        |
|---------|-------------------|--------------|----------------|
| 0.0.43 | 2025-12-09 | [70744](https://github.com/airbytehq/airbyte/pull/70744) | Update dependencies |
| 0.0.42 | 2025-11-25 | [70097](https://github.com/airbytehq/airbyte/pull/70097) | Update dependencies |
| 0.0.41 | 2025-11-18 | [69590](https://github.com/airbytehq/airbyte/pull/69590) | Update dependencies |
| 0.0.40 | 2025-10-29 | [69062](https://github.com/airbytehq/airbyte/pull/69062) | Update dependencies |
| 0.0.39 | 2025-10-21 | [68415](https://github.com/airbytehq/airbyte/pull/68415) | Update dependencies |
| 0.0.38 | 2025-10-14 | [67850](https://github.com/airbytehq/airbyte/pull/67850) | Update dependencies |
| 0.0.37 | 2025-10-07 | [67384](https://github.com/airbytehq/airbyte/pull/67384) | Update dependencies |
| 0.0.36 | 2025-09-30 | [66349](https://github.com/airbytehq/airbyte/pull/66349) | Update dependencies |
| 0.0.35 | 2025-09-09 | [65771](https://github.com/airbytehq/airbyte/pull/65771) | Update dependencies |
| 0.0.34 | 2025-09-05 | [65966](https://github.com/airbytehq/airbyte/pull/65966) | Update to CDK v7.0.0 |
| 0.0.33 | 2025-08-23 | [65185](https://github.com/airbytehq/airbyte/pull/65185) | Update dependencies |
| 0.0.32 | 2025-08-09 | [64745](https://github.com/airbytehq/airbyte/pull/64745) | Update dependencies |
| 0.0.31 | 2025-08-02 | [64178](https://github.com/airbytehq/airbyte/pull/64178) | Update dependencies |
| 0.0.30 | 2025-07-26 | [63909](https://github.com/airbytehq/airbyte/pull/63909) | Update dependencies |
| 0.0.29 | 2025-07-19 | [63390](https://github.com/airbytehq/airbyte/pull/63390) | Update dependencies |
| 0.0.28 | 2025-07-12 | [63120](https://github.com/airbytehq/airbyte/pull/63120) | Update dependencies |
| 0.0.27 | 2025-07-05 | [62651](https://github.com/airbytehq/airbyte/pull/62651) | Update dependencies |
| 0.0.26 | 2025-06-28 | [62175](https://github.com/airbytehq/airbyte/pull/62175) | Update dependencies |
| 0.0.25 | 2025-06-21 | [61856](https://github.com/airbytehq/airbyte/pull/61856) | Update dependencies |
| 0.0.24 | 2025-06-14 | [61099](https://github.com/airbytehq/airbyte/pull/61099) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60618](https://github.com/airbytehq/airbyte/pull/60618) | Update dependencies |
| 0.0.22 | 2025-05-10 | [59897](https://github.com/airbytehq/airbyte/pull/59897) | Update dependencies |
| 0.0.21 | 2025-05-03 | [59257](https://github.com/airbytehq/airbyte/pull/59257) | Update dependencies |
| 0.0.20 | 2025-04-26 | [58825](https://github.com/airbytehq/airbyte/pull/58825) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58163](https://github.com/airbytehq/airbyte/pull/58163) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57715](https://github.com/airbytehq/airbyte/pull/57715) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57087](https://github.com/airbytehq/airbyte/pull/57087) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56660](https://github.com/airbytehq/airbyte/pull/56660) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56062](https://github.com/airbytehq/airbyte/pull/56062) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55473](https://github.com/airbytehq/airbyte/pull/55473) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54829](https://github.com/airbytehq/airbyte/pull/54829) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54307](https://github.com/airbytehq/airbyte/pull/54307) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53842](https://github.com/airbytehq/airbyte/pull/53842) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53262](https://github.com/airbytehq/airbyte/pull/53262) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52761](https://github.com/airbytehq/airbyte/pull/52761) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52279](https://github.com/airbytehq/airbyte/pull/52279) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51781](https://github.com/airbytehq/airbyte/pull/51781) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51177](https://github.com/airbytehq/airbyte/pull/51177) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50620](https://github.com/airbytehq/airbyte/pull/50620) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50084](https://github.com/airbytehq/airbyte/pull/50084) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49626](https://github.com/airbytehq/airbyte/pull/49626) | Update dependencies |
| 0.0.2 | 2024-12-12 | [48963](https://github.com/airbytehq/airbyte/pull/48963) | Update dependencies |
| 0.0.1   | 2024-11-07 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
