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
