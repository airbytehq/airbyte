# cimis
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

## Streams
| Stream Name | Primary Key | Pagination | Supports Full Sync | Supports Incremental |
|-------------|-------------|------------|---------------------|----------------------|
| data | Julian | No pagination | ✅ |  ✅  |
| stations | StationNbr | No pagination | ✅ |  ❌  |
| spatial_zipcodes | ZipCode | No pagination | ✅ |  ❌  |
| station_zipcodes | StationNbr.ZipCode | No pagination | ✅ |  ❌  |

## Changelog

<details>
  <summary>Expand to review</summary>

| Version          | Date       | Subject        |
|------------------|------------|----------------|
| 0.0.1 | 2024-09-18 | Initial release by [@topefolorunso](https://github.com/topefolorunso) via Connector Builder|

</details>