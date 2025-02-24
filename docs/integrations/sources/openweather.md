# OpenWeather

## Overview

This source connector syncs data from the [OpenWeather One Call API](https://openweathermap.org/api/one-call-api). This API allows to obtain current and weather data from a geolocation expressed in latitude and longitude.

### Output schema

This source currently has a single stream, `openweather_one_call`. An example of the data outputted by this stream is available [here](https://openweathermap.org/api/one-call-api#example).

### Features

| Feature                           | Supported? |
| :-------------------------------- | :--------- |
| Full Refresh Sync - (append only) | Yes        |
| Incremental - Append Sync         | Yes        |
| Namespaces                        | No         |

## Getting started

### Requirements

- An OpenWeather API key
- Latitude and longitude of the location for which you want to get weather data

### Setup guide

Visit the [OpenWeather](https://openweathermap.org) to create a user account and obtain an API key. The _One Call API_ is available with the free plan.

## Rate limiting

The free plan allows 60 calls per minute and 1,000,000 calls per month, you won't get beyond these limits with existing Airbyte's sync frequencies.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.14 | 2025-02-23 | [54623](https://github.com/airbytehq/airbyte/pull/54623) | Update dependencies |
| 0.3.13 | 2025-02-15 | [53985](https://github.com/airbytehq/airbyte/pull/53985) | Update dependencies |
| 0.3.12 | 2025-02-08 | [53482](https://github.com/airbytehq/airbyte/pull/53482) | Update dependencies |
| 0.3.11 | 2025-02-01 | [53011](https://github.com/airbytehq/airbyte/pull/53011) | Update dependencies |
| 0.3.10 | 2025-01-25 | [52513](https://github.com/airbytehq/airbyte/pull/52513) | Update dependencies |
| 0.3.9 | 2025-01-18 | [51858](https://github.com/airbytehq/airbyte/pull/51858) | Update dependencies |
| 0.3.8 | 2025-01-11 | [51336](https://github.com/airbytehq/airbyte/pull/51336) | Update dependencies |
| 0.3.7 | 2024-12-28 | [50733](https://github.com/airbytehq/airbyte/pull/50733) | Update dependencies |
| 0.3.6 | 2024-12-21 | [50258](https://github.com/airbytehq/airbyte/pull/50258) | Update dependencies |
| 0.3.5 | 2024-12-14 | [49707](https://github.com/airbytehq/airbyte/pull/49707) | Update dependencies |
| 0.3.4 | 2024-12-12 | [49332](https://github.com/airbytehq/airbyte/pull/49332) | Update dependencies |
| 0.3.3 | 2024-12-10 | [48871](https://github.com/airbytehq/airbyte/pull/48871) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.2 | 2024-10-29 | [47791](https://github.com/airbytehq/airbyte/pull/47791) | Update dependencies |
| 0.3.1 | 2024-10-08 | [46652](https://github.com/airbytehq/airbyte/pull/46652) | Fix longitude regex matching |
| 0.3.0 | 2024-08-26 | [44772](https://github.com/airbytehq/airbyte/pull/44772) | Refactor connector to manifest-only format |
| 0.2.17 | 2024-08-24 | [44725](https://github.com/airbytehq/airbyte/pull/44725) | Update dependencies |
| 0.2.16 | 2024-08-17 | [44236](https://github.com/airbytehq/airbyte/pull/44236) | Update dependencies |
| 0.2.15 | 2024-08-12 | [43735](https://github.com/airbytehq/airbyte/pull/43735) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43217](https://github.com/airbytehq/airbyte/pull/43217) | Update dependencies |
| 0.2.13 | 2024-07-27 | [42731](https://github.com/airbytehq/airbyte/pull/42731) | Update dependencies |
| 0.2.12 | 2024-07-20 | [42389](https://github.com/airbytehq/airbyte/pull/42389) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41814](https://github.com/airbytehq/airbyte/pull/41814) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41592](https://github.com/airbytehq/airbyte/pull/41592) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41199](https://github.com/airbytehq/airbyte/pull/41199) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40784](https://github.com/airbytehq/airbyte/pull/40784) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40408](https://github.com/airbytehq/airbyte/pull/40408) | Update dependencies |
| 0.2.6 | 2024-06-22 | [40005](https://github.com/airbytehq/airbyte/pull/40005) | Update dependencies |
| 0.2.5 | 2024-06-06 | [39170](https://github.com/airbytehq/airbyte/pull/39170) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-05-25 | [38601](https://github.com/airbytehq/airbyte/pull/38601) | Make compatible with the builder. |
| 0.2.3 | 2024-04-19 | [37209](https://github.com/airbytehq/airbyte/pull/37209) | Upgrade to CDK 0.80.0 and manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37209](https://github.com/airbytehq/airbyte/pull/37209) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37209](https://github.com/airbytehq/airbyte/pull/37209) | schema descriptions |
| 0.2.0 | 2023-08-31 | [29983](https://github.com/airbytehq/airbyte/pull/29983) | Migrate to Low Code Framework |
| 0.1.6 | 2022-06-21 | [16136](https://github.com/airbytehq/airbyte/pull/16136) | Update openweather onecall api to 3.0. |
| 0.1.5 | 2022-06-21 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | No changes. Used connector to test publish workflow changes. |
| 0.1.4 | 2022-04-27 | [12397](https://github.com/airbytehq/airbyte/pull/12397) | No changes. Used connector to test publish workflow changes. |
| 0.1.0 | 2021-10-27 | [7434](https://github.com/airbytehq/airbyte/pull/7434) | Initial release |

</details>
