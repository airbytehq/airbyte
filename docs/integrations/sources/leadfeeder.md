# Leadfeeder

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_token` | `string` | Leadfeeder API token.  |  |
| `start_date` | `string` | Start date for incremental syncs. Records that were updated before that date will not be synced.  |  |

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| `accounts` | `id` | No pagination | ✅ |  ❌  |
| `leads` | `id` | DefaultPaginator | ✅ |  ✅  |
| `visits` | `id` | DefaultPaginator | ✅ |  ✅  |


## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.45 | 2025-12-09 | [70747](https://github.com/airbytehq/airbyte/pull/70747) | Update dependencies |
| 0.0.44 | 2025-11-25 | [70011](https://github.com/airbytehq/airbyte/pull/70011) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69455](https://github.com/airbytehq/airbyte/pull/69455) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68969](https://github.com/airbytehq/airbyte/pull/68969) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68295](https://github.com/airbytehq/airbyte/pull/68295) | Update dependencies |
| 0.0.40 | 2025-10-14 | [68021](https://github.com/airbytehq/airbyte/pull/68021) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67528](https://github.com/airbytehq/airbyte/pull/67528) | Update dependencies |
| 0.0.38 | 2025-09-30 | [66810](https://github.com/airbytehq/airbyte/pull/66810) | Update dependencies |
| 0.0.37 | 2025-09-24 | [66649](https://github.com/airbytehq/airbyte/pull/66649) | Update dependencies |
| 0.0.36 | 2025-09-09 | [66102](https://github.com/airbytehq/airbyte/pull/66102) | Update dependencies |
| 0.0.35 | 2025-08-23 | [65309](https://github.com/airbytehq/airbyte/pull/65309) | Update dependencies |
| 0.0.34 | 2025-08-09 | [64601](https://github.com/airbytehq/airbyte/pull/64601) | Update dependencies |
| 0.0.33 | 2025-08-02 | [64269](https://github.com/airbytehq/airbyte/pull/64269) | Update dependencies |
| 0.0.32 | 2025-07-26 | [63836](https://github.com/airbytehq/airbyte/pull/63836) | Update dependencies |
| 0.0.31 | 2025-07-19 | [63500](https://github.com/airbytehq/airbyte/pull/63500) | Update dependencies |
| 0.0.30 | 2025-07-12 | [63103](https://github.com/airbytehq/airbyte/pull/63103) | Update dependencies |
| 0.0.29 | 2025-07-05 | [62567](https://github.com/airbytehq/airbyte/pull/62567) | Update dependencies |
| 0.0.28 | 2025-06-28 | [62170](https://github.com/airbytehq/airbyte/pull/62170) | Update dependencies |
| 0.0.27 | 2025-06-21 | [61791](https://github.com/airbytehq/airbyte/pull/61791) | Update dependencies |
| 0.0.26 | 2025-06-14 | [60714](https://github.com/airbytehq/airbyte/pull/60714) | Update dependencies |
| 0.0.25 | 2025-05-10 | [59779](https://github.com/airbytehq/airbyte/pull/59779) | Update dependencies |
| 0.0.24 | 2025-05-03 | [59282](https://github.com/airbytehq/airbyte/pull/59282) | Update dependencies |
| 0.0.23 | 2025-04-26 | [58822](https://github.com/airbytehq/airbyte/pull/58822) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58216](https://github.com/airbytehq/airbyte/pull/58216) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57686](https://github.com/airbytehq/airbyte/pull/57686) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57052](https://github.com/airbytehq/airbyte/pull/57052) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56688](https://github.com/airbytehq/airbyte/pull/56688) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56080](https://github.com/airbytehq/airbyte/pull/56080) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55488](https://github.com/airbytehq/airbyte/pull/55488) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54820](https://github.com/airbytehq/airbyte/pull/54820) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54359](https://github.com/airbytehq/airbyte/pull/54359) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53795](https://github.com/airbytehq/airbyte/pull/53795) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53277](https://github.com/airbytehq/airbyte/pull/53277) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52733](https://github.com/airbytehq/airbyte/pull/52733) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52281](https://github.com/airbytehq/airbyte/pull/52281) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51811](https://github.com/airbytehq/airbyte/pull/51811) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51217](https://github.com/airbytehq/airbyte/pull/51217) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50144](https://github.com/airbytehq/airbyte/pull/50144) | Update dependencies |
| 0.0.7 | 2024-12-14 | [49624](https://github.com/airbytehq/airbyte/pull/49624) | Update dependencies |
| 0.0.6 | 2024-12-12 | [49244](https://github.com/airbytehq/airbyte/pull/49244) | Update dependencies |
| 0.0.5 | 2024-12-11 | [48909](https://github.com/airbytehq/airbyte/pull/48909) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.4 | 2024-11-04 | [48292](https://github.com/airbytehq/airbyte/pull/48292) | Update dependencies |
| 0.0.3 | 2024-10-29 | [47916](https://github.com/airbytehq/airbyte/pull/47916) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47617](https://github.com/airbytehq/airbyte/pull/47617) | Update dependencies |
| 0.0.1 | 2024-08-21 | | Initial release by natikgadzhi via Connector Builder |

</details>
