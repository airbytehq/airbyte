# Tinyemail
Tinyemail is an email marketing tool.
We can extract data from campaigns and contacts streams using this connector.
[API Docs](https://docs.tinyemail.com/docs/tiny-email/tinyemail)

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| campaigns | id | DefaultPaginator | ✅ |  ❌  |
| contacts | id | No pagination | ✅ |  ❌  |
| sender_details | id | No pagination | ✅ |  ❌  |
| contact_members |  | DefaultPaginator | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.39 | 2025-12-09 | [70760](https://github.com/airbytehq/airbyte/pull/70760) | Update dependencies |
| 0.0.38 | 2025-11-25 | [69897](https://github.com/airbytehq/airbyte/pull/69897) | Update dependencies |
| 0.0.37 | 2025-11-18 | [69666](https://github.com/airbytehq/airbyte/pull/69666) | Update dependencies |
| 0.0.36 | 2025-10-29 | [68846](https://github.com/airbytehq/airbyte/pull/68846) | Update dependencies |
| 0.0.35 | 2025-10-21 | [68561](https://github.com/airbytehq/airbyte/pull/68561) | Update dependencies |
| 0.0.34 | 2025-10-14 | [67857](https://github.com/airbytehq/airbyte/pull/67857) | Update dependencies |
| 0.0.33 | 2025-10-07 | [67506](https://github.com/airbytehq/airbyte/pull/67506) | Update dependencies |
| 0.0.32 | 2025-09-30 | [66832](https://github.com/airbytehq/airbyte/pull/66832) | Update dependencies |
| 0.0.31 | 2025-09-23 | [66603](https://github.com/airbytehq/airbyte/pull/66603) | Update dependencies |
| 0.0.30 | 2025-09-09 | [65737](https://github.com/airbytehq/airbyte/pull/65737) | Update dependencies |
| 0.0.29 | 2025-08-24 | [65470](https://github.com/airbytehq/airbyte/pull/65470) | Update dependencies |
| 0.0.28 | 2025-08-09 | [64872](https://github.com/airbytehq/airbyte/pull/64872) | Update dependencies |
| 0.0.27 | 2025-08-02 | [64442](https://github.com/airbytehq/airbyte/pull/64442) | Update dependencies |
| 0.0.26 | 2025-07-20 | [63676](https://github.com/airbytehq/airbyte/pull/63676) | Update dependencies |
| 0.0.25 | 2025-07-12 | [63060](https://github.com/airbytehq/airbyte/pull/63060) | Update dependencies |
| 0.0.24 | 2025-06-28 | [62252](https://github.com/airbytehq/airbyte/pull/62252) | Update dependencies |
| 0.0.23 | 2025-06-14 | [61610](https://github.com/airbytehq/airbyte/pull/61610) | Update dependencies |
| 0.0.22 | 2025-05-24 | [60090](https://github.com/airbytehq/airbyte/pull/60090) | Update dependencies |
| 0.0.21 | 2025-05-04 | [59641](https://github.com/airbytehq/airbyte/pull/59641) | Update dependencies |
| 0.0.20 | 2025-04-27 | [58989](https://github.com/airbytehq/airbyte/pull/58989) | Update dependencies |
| 0.0.19 | 2025-04-19 | [58411](https://github.com/airbytehq/airbyte/pull/58411) | Update dependencies |
| 0.0.18 | 2025-04-12 | [57943](https://github.com/airbytehq/airbyte/pull/57943) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57484](https://github.com/airbytehq/airbyte/pull/57484) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56858](https://github.com/airbytehq/airbyte/pull/56858) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56254](https://github.com/airbytehq/airbyte/pull/56254) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55617](https://github.com/airbytehq/airbyte/pull/55617) | Update dependencies |
| 0.0.13 | 2025-03-01 | [55101](https://github.com/airbytehq/airbyte/pull/55101) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54541](https://github.com/airbytehq/airbyte/pull/54541) | Update dependencies |
| 0.0.11 | 2025-02-15 | [54102](https://github.com/airbytehq/airbyte/pull/54102) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53527](https://github.com/airbytehq/airbyte/pull/53527) | Update dependencies |
| 0.0.9 | 2025-02-01 | [53059](https://github.com/airbytehq/airbyte/pull/53059) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52443](https://github.com/airbytehq/airbyte/pull/52443) | Update dependencies |
| 0.0.7 | 2025-01-18 | [52016](https://github.com/airbytehq/airbyte/pull/52016) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51424](https://github.com/airbytehq/airbyte/pull/51424) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50815](https://github.com/airbytehq/airbyte/pull/50815) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50340](https://github.com/airbytehq/airbyte/pull/50340) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49779](https://github.com/airbytehq/airbyte/pull/49779) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49437](https://github.com/airbytehq/airbyte/pull/49437) | Update dependencies |
| 0.0.1 | 2024-11-08 | | Initial release by [@ombhardwajj](https://github.com/ombhardwajj) via Connector Builder |

</details>
