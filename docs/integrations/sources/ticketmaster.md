# Ticketmaster

Buy and sell tickets online for concerts, sports, theater, family and other events near you from Ticketmaster.

[TicketMaster API Documentation](https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/#search-classifications-v2)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| events | id | DefaultPaginator | ✅ |  ❌  |
| attractions | id | DefaultPaginator | ✅ |  ❌  |
| venues | id | DefaultPaginator | ✅ |  ❌  |
| suggest | id | No pagination | ✅ |  ❌  |
| event_images | id | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.40 | 2025-12-09 | [70763](https://github.com/airbytehq/airbyte/pull/70763) | Update dependencies |
| 0.0.39 | 2025-11-25 | [69870](https://github.com/airbytehq/airbyte/pull/69870) | Update dependencies |
| 0.0.38 | 2025-11-18 | [69656](https://github.com/airbytehq/airbyte/pull/69656) | Update dependencies |
| 0.0.37 | 2025-10-29 | [69039](https://github.com/airbytehq/airbyte/pull/69039) | Update dependencies |
| 0.0.36 | 2025-10-21 | [68528](https://github.com/airbytehq/airbyte/pull/68528) | Update dependencies |
| 0.0.35 | 2025-10-14 | [67879](https://github.com/airbytehq/airbyte/pull/67879) | Update dependencies |
| 0.0.34 | 2025-10-07 | [67467](https://github.com/airbytehq/airbyte/pull/67467) | Update dependencies |
| 0.0.33 | 2025-09-30 | [66875](https://github.com/airbytehq/airbyte/pull/66875) | Update dependencies |
| 0.0.32 | 2025-09-23 | [66360](https://github.com/airbytehq/airbyte/pull/66360) | Update dependencies |
| 0.0.31 | 2025-09-09 | [65685](https://github.com/airbytehq/airbyte/pull/65685) | Update dependencies |
| 0.0.30 | 2025-08-24 | [65496](https://github.com/airbytehq/airbyte/pull/65496) | Update dependencies |
| 0.0.29 | 2025-08-16 | [65039](https://github.com/airbytehq/airbyte/pull/65039) | Update dependencies |
| 0.0.28 | 2025-08-02 | [64475](https://github.com/airbytehq/airbyte/pull/64475) | Update dependencies |
| 0.0.27 | 2025-07-19 | [63615](https://github.com/airbytehq/airbyte/pull/63615) | Update dependencies |
| 0.0.26 | 2025-07-12 | [63083](https://github.com/airbytehq/airbyte/pull/63083) | Update dependencies |
| 0.0.25 | 2025-06-28 | [62288](https://github.com/airbytehq/airbyte/pull/62288) | Update dependencies |
| 0.0.24 | 2025-06-14 | [60567](https://github.com/airbytehq/airbyte/pull/60567) | Update dependencies |
| 0.0.23 | 2025-05-10 | [60161](https://github.com/airbytehq/airbyte/pull/60161) | Update dependencies |
| 0.0.22 | 2025-05-04 | [59629](https://github.com/airbytehq/airbyte/pull/59629) | Update dependencies |
| 0.0.21 | 2025-04-27 | [58978](https://github.com/airbytehq/airbyte/pull/58978) | Update dependencies |
| 0.0.20 | 2025-04-19 | [58379](https://github.com/airbytehq/airbyte/pull/58379) | Update dependencies |
| 0.0.19 | 2025-04-12 | [57946](https://github.com/airbytehq/airbyte/pull/57946) | Update dependencies |
| 0.0.18 | 2025-04-05 | [56900](https://github.com/airbytehq/airbyte/pull/56900) | Update dependencies |
| 0.0.17 | 2025-03-22 | [56243](https://github.com/airbytehq/airbyte/pull/56243) | Update dependencies |
| 0.0.16 | 2025-03-08 | [55607](https://github.com/airbytehq/airbyte/pull/55607) | Update dependencies |
| 0.0.15 | 2025-03-01 | [55128](https://github.com/airbytehq/airbyte/pull/55128) | Update dependencies |
| 0.0.14 | 2025-02-22 | [54516](https://github.com/airbytehq/airbyte/pull/54516) | Update dependencies |
| 0.0.13 | 2025-02-15 | [54073](https://github.com/airbytehq/airbyte/pull/54073) | Update dependencies |
| 0.0.12 | 2025-02-08 | [53543](https://github.com/airbytehq/airbyte/pull/53543) | Update dependencies |
| 0.0.11 | 2025-02-01 | [53094](https://github.com/airbytehq/airbyte/pull/53094) | Update dependencies |
| 0.0.10 | 2025-01-25 | [52422](https://github.com/airbytehq/airbyte/pull/52422) | Update dependencies |
| 0.0.9 | 2025-01-18 | [52005](https://github.com/airbytehq/airbyte/pull/52005) | Update dependencies |
| 0.0.8 | 2025-01-11 | [51389](https://github.com/airbytehq/airbyte/pull/51389) | Update dependencies |
| 0.0.7 | 2024-12-28 | [50795](https://github.com/airbytehq/airbyte/pull/50795) | Update dependencies |
| 0.0.6 | 2024-12-21 | [50368](https://github.com/airbytehq/airbyte/pull/50368) | Update dependencies |
| 0.0.5 | 2024-12-14 | [49773](https://github.com/airbytehq/airbyte/pull/49773) | Update dependencies |
| 0.0.4 | 2024-12-12 | [49412](https://github.com/airbytehq/airbyte/pull/49412) | Update dependencies |
| 0.0.3 | 2024-12-11 | [49123](https://github.com/airbytehq/airbyte/pull/49123) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.2 | 2024-11-04 | [48297](https://github.com/airbytehq/airbyte/pull/48297) | Update dependencies |
| 0.0.1 | 2024-10-21 | | Initial release by [@gemsteam](https://github.com/gemsteam) via Connector Builder |

</details>
