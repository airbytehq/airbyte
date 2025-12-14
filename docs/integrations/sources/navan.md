# Navan

The Navan connector supports travel booking data such as hotels and flights. 

## Prerequisites

* Client ID and Client Secret - Credentials for accessing the Navan API that can be created by administrators. 
  * Learn how to create these API credentials by following [documentation provided by Navan](https://app.navan.com/app/helpcenter/articles/travel/admin/other-integrations/booking-data-integration). Note that API credential details are only accessible once.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `client_id` | `string` | OAuth Client ID.  |  |
| `client_secret` | `string` | OAuth Client Secret.  |  |
| `start_date` | `string` | Start date.  |  |

## Streams

| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| bookings | uuid | DefaultPaginator | ✅ |  ✅  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date              | Pull Request | Subject        |
|------------------|-------------------|--------------|----------------|
| 0.0.38 | 2025-12-09 | [70539](https://github.com/airbytehq/airbyte/pull/70539) | Update dependencies |
| 0.0.37 | 2025-11-25 | [69866](https://github.com/airbytehq/airbyte/pull/69866) | Update dependencies |
| 0.0.36 | 2025-11-18 | [69397](https://github.com/airbytehq/airbyte/pull/69397) | Update dependencies |
| 0.0.35 | 2025-10-29 | [68724](https://github.com/airbytehq/airbyte/pull/68724) | Update dependencies |
| 0.0.34 | 2025-10-21 | [68377](https://github.com/airbytehq/airbyte/pull/68377) | Update dependencies |
| 0.0.33 | 2025-10-14 | [67784](https://github.com/airbytehq/airbyte/pull/67784) | Update dependencies |
| 0.0.32 | 2025-10-07 | [67426](https://github.com/airbytehq/airbyte/pull/67426) | Update dependencies |
| 0.0.31 | 2025-09-30 | [66936](https://github.com/airbytehq/airbyte/pull/66936) | Update dependencies |
| 0.0.30 | 2025-09-23 | [66619](https://github.com/airbytehq/airbyte/pull/66619) | Update dependencies |
| 0.0.29 | 2025-09-09 | [65843](https://github.com/airbytehq/airbyte/pull/65843) | Update dependencies |
| 0.0.28 | 2025-08-23 | [65184](https://github.com/airbytehq/airbyte/pull/65184) | Update dependencies |
| 0.0.27 | 2025-08-09 | [64720](https://github.com/airbytehq/airbyte/pull/64720) | Update dependencies |
| 0.0.26 | 2025-08-02 | [64272](https://github.com/airbytehq/airbyte/pull/64272) | Update dependencies |
| 0.0.25 | 2025-07-26 | [63819](https://github.com/airbytehq/airbyte/pull/63819) | Update dependencies |
| 0.0.24 | 2025-07-19 | [63419](https://github.com/airbytehq/airbyte/pull/63419) | Update dependencies |
| 0.0.23 | 2025-07-12 | [63208](https://github.com/airbytehq/airbyte/pull/63208) | Update dependencies |
| 0.0.22 | 2025-07-05 | [62545](https://github.com/airbytehq/airbyte/pull/62545) | Update dependencies |
| 0.0.21 | 2025-06-28 | [62308](https://github.com/airbytehq/airbyte/pull/62308) | Update dependencies |
| 0.0.20 | 2025-06-21 | [61069](https://github.com/airbytehq/airbyte/pull/61069) | Update dependencies |
| 0.0.19 | 2025-05-24 | [60511](https://github.com/airbytehq/airbyte/pull/60511) | Update dependencies |
| 0.0.18 | 2025-05-10 | [57894](https://github.com/airbytehq/airbyte/pull/57894) | Update dependencies |
| 0.0.17 | 2025-04-05 | [57297](https://github.com/airbytehq/airbyte/pull/57297) | Update dependencies |
| 0.0.16 | 2025-03-29 | [56691](https://github.com/airbytehq/airbyte/pull/56691) | Update dependencies |
| 0.0.15 | 2025-03-22 | [56027](https://github.com/airbytehq/airbyte/pull/56027) | Update dependencies |
| 0.0.14 | 2025-03-08 | [55457](https://github.com/airbytehq/airbyte/pull/55457) | Update dependencies |
| 0.0.13 | 2025-03-01 | [54765](https://github.com/airbytehq/airbyte/pull/54765) | Update dependencies |
| 0.0.12 | 2025-02-22 | [54310](https://github.com/airbytehq/airbyte/pull/54310) | Update dependencies |
| 0.0.11 | 2025-02-15 | [53857](https://github.com/airbytehq/airbyte/pull/53857) | Update dependencies |
| 0.0.10 | 2025-02-08 | [53252](https://github.com/airbytehq/airbyte/pull/53252) | Update dependencies |
| 0.0.9 | 2025-02-01 | [52743](https://github.com/airbytehq/airbyte/pull/52743) | Update dependencies |
| 0.0.8 | 2025-01-25 | [52270](https://github.com/airbytehq/airbyte/pull/52270) | Update dependencies |
| 0.0.7 | 2025-01-18 | [51799](https://github.com/airbytehq/airbyte/pull/51799) | Update dependencies |
| 0.0.6 | 2025-01-11 | [51174](https://github.com/airbytehq/airbyte/pull/51174) | Update dependencies |
| 0.0.5 | 2024-12-28 | [50642](https://github.com/airbytehq/airbyte/pull/50642) | Update dependencies |
| 0.0.4 | 2024-12-21 | [50106](https://github.com/airbytehq/airbyte/pull/50106) | Update dependencies |
| 0.0.3 | 2024-12-14 | [49599](https://github.com/airbytehq/airbyte/pull/49599) | Update dependencies |
| 0.0.2 | 2024-12-12 | [49217](https://github.com/airbytehq/airbyte/pull/49217) | Update dependencies |
| 0.0.1 | 2024-11-26 | | Initial release by [@matteogp](https://github.com/matteogp) via Connector Builder |

</details>
