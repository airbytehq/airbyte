# CIMIS
The California Irrigation Management Information System (CIMIS) is a program unit in the Water Use and Efficiency Branch, Division of Regional Assistance, California Department of Water Resources (DWR) that manages a network of over 145 automated weather stations in California. CIMIS was developed in 1982 by DWR and the University of California, Davis (UC Davis). It was designed to assist irrigators in managing their water resources more efficiently. Efficient use of water resources benefits Californians by saving water, energy, and money.

## Configuration

| Input | Type | Description | Default Value |
|-------|------|-------------|---------------|
| `api_key` | `string` | API Key.  |  |
| `targets_type` | `string` | Targets Type.  |  |
| `targets` | `array` | Targets.  |  |
| `daily_data_items` | `array` | Daily Data Items.  |  |
| `hourly_data_items` | `array` | Hourly Data Items.  |  |
| `start_date` | `string` | Start date.  |  |
| `end_date` | `string` | End date.  |  |
| `unit_of_measure` | `string` | Unit of Measure.  |  |

To get started, register and request your appKey from the [CIMIS website](https://wwwcimis.water.ca.gov/). You will receive an application key (aka appKey).

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| data | Julian | No pagination | ✅ |  ✅  |
| stations | StationNbr | No pagination | ✅ |  ❌  |
| spatial_zipcodes | ZipCode | No pagination | ✅ |  ❌  |
| station_zipcodes | StationNbr.ZipCode | No pagination | ✅ |  ❌  |

⚠️ Note that `Juilan` in the `data` stream represents the day (in Julia format).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
|---------|------|--------------|---------|
| 0.0.45 | 2025-12-09 | [70607](https://github.com/airbytehq/airbyte/pull/70607) | Update dependencies |
| 0.0.44 | 2025-11-25 | [69926](https://github.com/airbytehq/airbyte/pull/69926) | Update dependencies |
| 0.0.43 | 2025-11-18 | [69600](https://github.com/airbytehq/airbyte/pull/69600) | Update dependencies |
| 0.0.42 | 2025-10-29 | [68897](https://github.com/airbytehq/airbyte/pull/68897) | Update dependencies |
| 0.0.41 | 2025-10-21 | [68523](https://github.com/airbytehq/airbyte/pull/68523) | Update dependencies |
| 0.0.40 | 2025-10-14 | [68047](https://github.com/airbytehq/airbyte/pull/68047) | Update dependencies |
| 0.0.39 | 2025-10-07 | [67177](https://github.com/airbytehq/airbyte/pull/67177) | Update dependencies |
| 0.0.38 | 2025-09-30 | [66246](https://github.com/airbytehq/airbyte/pull/66246) | Update dependencies |
| 0.0.37 | 2025-09-09 | [65880](https://github.com/airbytehq/airbyte/pull/65880) | Update dependencies |
| 0.0.36 | 2025-08-23 | [65256](https://github.com/airbytehq/airbyte/pull/65256) | Update dependencies |
| 0.0.35 | 2025-08-09 | [64774](https://github.com/airbytehq/airbyte/pull/64774) | Update dependencies |
| 0.0.34 | 2025-08-02 | [64353](https://github.com/airbytehq/airbyte/pull/64353) | Update dependencies |
| 0.0.33 | 2025-07-26 | [64010](https://github.com/airbytehq/airbyte/pull/64010) | Update dependencies |
| 0.0.32 | 2025-07-19 | [63594](https://github.com/airbytehq/airbyte/pull/63594) | Update dependencies |
| 0.0.31 | 2025-07-12 | [63004](https://github.com/airbytehq/airbyte/pull/63004) | Update dependencies |
| 0.0.30 | 2025-07-05 | [62774](https://github.com/airbytehq/airbyte/pull/62774) | Update dependencies |
| 0.0.29 | 2025-06-28 | [62421](https://github.com/airbytehq/airbyte/pull/62421) | Update dependencies |
| 0.0.28 | 2025-06-22 | [62004](https://github.com/airbytehq/airbyte/pull/62004) | Update dependencies |
| 0.0.27 | 2025-06-14 | [61200](https://github.com/airbytehq/airbyte/pull/61200) | Update dependencies |
| 0.0.26 | 2025-05-24 | [60357](https://github.com/airbytehq/airbyte/pull/60357) | Update dependencies |
| 0.0.25 | 2025-05-10 | [60044](https://github.com/airbytehq/airbyte/pull/60044) | Update dependencies |
| 0.0.24 | 2025-05-03 | [59427](https://github.com/airbytehq/airbyte/pull/59427) | Update dependencies |
| 0.0.23 | 2025-04-26 | [58898](https://github.com/airbytehq/airbyte/pull/58898) | Update dependencies |
| 0.0.22 | 2025-04-19 | [58348](https://github.com/airbytehq/airbyte/pull/58348) | Update dependencies |
| 0.0.21 | 2025-04-12 | [57764](https://github.com/airbytehq/airbyte/pull/57764) | Update dependencies |
| 0.0.20 | 2025-04-05 | [57172](https://github.com/airbytehq/airbyte/pull/57172) | Update dependencies |
| 0.0.19 | 2025-03-29 | [56611](https://github.com/airbytehq/airbyte/pull/56611) | Update dependencies |
| 0.0.18 | 2025-03-22 | [56103](https://github.com/airbytehq/airbyte/pull/56103) | Update dependencies |
| 0.0.17 | 2025-03-08 | [55370](https://github.com/airbytehq/airbyte/pull/55370) | Update dependencies |
| 0.0.16 | 2025-03-01 | [54876](https://github.com/airbytehq/airbyte/pull/54876) | Update dependencies |
| 0.0.15 | 2025-02-22 | [54263](https://github.com/airbytehq/airbyte/pull/54263) | Update dependencies |
| 0.0.14 | 2025-02-15 | [53908](https://github.com/airbytehq/airbyte/pull/53908) | Update dependencies |
| 0.0.13 | 2025-02-08 | [53437](https://github.com/airbytehq/airbyte/pull/53437) | Update dependencies |
| 0.0.12 | 2025-02-01 | [52947](https://github.com/airbytehq/airbyte/pull/52947) | Update dependencies |
| 0.0.11 | 2025-01-25 | [52158](https://github.com/airbytehq/airbyte/pull/52158) | Update dependencies |
| 0.0.10 | 2025-01-18 | [51713](https://github.com/airbytehq/airbyte/pull/51713) | Update dependencies |
| 0.0.9 | 2025-01-11 | [51236](https://github.com/airbytehq/airbyte/pull/51236) | Update dependencies |
| 0.0.8 | 2024-12-28 | [50453](https://github.com/airbytehq/airbyte/pull/50453) | Update dependencies |
| 0.0.7 | 2024-12-21 | [50154](https://github.com/airbytehq/airbyte/pull/50154) | Update dependencies |
| 0.0.6 | 2024-12-14 | [49565](https://github.com/airbytehq/airbyte/pull/49565) | Update dependencies |
| 0.0.5 | 2024-12-12 | [49281](https://github.com/airbytehq/airbyte/pull/49281) | Update dependencies |
| 0.0.4 | 2024-12-11 | [49024](https://github.com/airbytehq/airbyte/pull/49024) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.0.3 | 2024-11-04 | [48156](https://github.com/airbytehq/airbyte/pull/48156) | Update dependencies |
| 0.0.2 | 2024-10-28 | [47556](https://github.com/airbytehq/airbyte/pull/47556) | Update dependencies |
| 0.0.1 | 2024-09-18 | | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder |

</details>
