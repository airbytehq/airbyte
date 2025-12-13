# Smartreach
Smartreach is a sales engagement platform.
Using this connector we extract data from two streams : campaigns and prospects.
Docs : https://smartreach.io/api_docs#smartreach-api

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `teamid` | `number` | TeamID.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | id | No pagination | ✅ |  ❌  |
| prospects |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.38 | 2025-12-09 | [70720](https://github.com/airbytehq/airbyte/pull/70720) | Update dependencies |
| 0.0.37 | 2025-11-25 | [70103](https://github.com/airbytehq/airbyte/pull/70103) | Update dependencies |
| 0.0.36 | 2025-11-18 | [69448](https://github.com/airbytehq/airbyte/pull/69448) | Update dependencies |
| 0.0.35 | 2025-10-29 | [68828](https://github.com/airbytehq/airbyte/pull/68828) | Update dependencies |
| 0.0.34 | 2025-10-21 | [68280](https://github.com/airbytehq/airbyte/pull/68280) | Update dependencies |
| 0.0.33 | 2025-10-14 | [67763](https://github.com/airbytehq/airbyte/pull/67763) | Update dependencies |
| 0.0.32 | 2025-10-07 | [67431](https://github.com/airbytehq/airbyte/pull/67431) | Update dependencies |
| 0.0.31 | 2025-09-30 | [66917](https://github.com/airbytehq/airbyte/pull/66917) | Update dependencies |
| 0.0.30 | 2025-09-24 | [66260](https://github.com/airbytehq/airbyte/pull/66260) | Update dependencies |
| 0.0.29 | 2025-08-24 | [65498](https://github.com/airbytehq/airbyte/pull/65498) | Update dependencies |
| 0.0.28 | 2025-08-16 | [64997](https://github.com/airbytehq/airbyte/pull/64997) | Update dependencies |
| 0.0.27 | 2025-08-02 | [64424](https://github.com/airbytehq/airbyte/pull/64424) | Update dependencies |
| 0.0.26 | 2025-07-26 | [63991](https://github.com/airbytehq/airbyte/pull/63991) | Update dependencies |
| 0.0.25 | 2025-07-05 | [62704](https://github.com/airbytehq/airbyte/pull/62704) | Update dependencies |
| 0.0.24 | 2025-06-28 | [61302](https://github.com/airbytehq/airbyte/pull/61302) | Update dependencies |
| 0.0.23 | 2025-05-24 | [60555](https://github.com/airbytehq/airbyte/pull/60555) | Update dependencies |
| 0.0.22 | 2025-05-10 | [60177](https://github.com/airbytehq/airbyte/pull/60177) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59614](https://github.com/airbytehq/airbyte/pull/59614) | Update dependencies |
| 0.0.20 | 2025-04-27 | [58439](https://github.com/airbytehq/airbyte/pull/58439) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57934](https://github.com/airbytehq/airbyte/pull/57934) | Update dependencies |
| 0.0.18 | 2025-04-05 | [57434](https://github.com/airbytehq/airbyte/pull/57434) | Update dependencies |
| 0.0.17 | 2025-03-29 | [56846](https://github.com/airbytehq/airbyte/pull/56846) | Update dependencies |
| 0.0.16 | 2025-03-22 | [56252](https://github.com/airbytehq/airbyte/pull/56252) | Update dependencies |
| 0.0.15 | 2025-03-08 | [55582](https://github.com/airbytehq/airbyte/pull/55582) | Update dependencies |
| 0.0.14 | 2025-03-01 | [55136](https://github.com/airbytehq/airbyte/pull/55136) | Update dependencies |
| 0.0.13 | 2025-02-22 | [54480](https://github.com/airbytehq/airbyte/pull/54480) | Update dependencies |
| 0.0.12 | 2025-02-15 | [54098](https://github.com/airbytehq/airbyte/pull/54098) | Update dependencies |
| 0.0.11 | 2025-02-08 | [53577](https://github.com/airbytehq/airbyte/pull/53577) | Update dependencies |
| 0.0.10 | 2025-02-01 | [53082](https://github.com/airbytehq/airbyte/pull/53082) | Update dependencies |
| 0.0.9 | 2025-01-25 | [52394](https://github.com/airbytehq/airbyte/pull/52394) | Update dependencies |
| 0.0.8 | 2025-01-18 | [51995](https://github.com/airbytehq/airbyte/pull/51995) | Update dependencies |
| 0.0.7 | 2025-01-11 | [51379](https://github.com/airbytehq/airbyte/pull/51379) | Update dependencies |
| 0.0.6 | 2024-12-28 | [50814](https://github.com/airbytehq/airbyte/pull/50814) | Update dependencies |
| 0.0.5 | 2024-12-21 | [50351](https://github.com/airbytehq/airbyte/pull/50351) | Update dependencies |
| 0.0.4 | 2024-12-14 | [49749](https://github.com/airbytehq/airbyte/pull/49749) | Update dependencies |
| 0.0.3 | 2024-12-12 | [49406](https://github.com/airbytehq/airbyte/pull/49406) | Update dependencies |
| 0.0.2 | 2024-12-11 | [49113](https://github.com/airbytehq/airbyte/pull/49113) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.1 | 2024-11-01 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
