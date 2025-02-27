# Weatherstack

## Overview

This source connector syncs data from the [Weatherstack API](http://api.weatherstack.com/). This API allows to obtain current, historical, location lookup, and weather forecast.

### Output schema

This source currently has four streams: `current`, `historical`, `forecast`, and `autocomplete`. The Current Weather API is available on all plans. The Historical Weather and Autocomplete API's are available on the standard plan and higher. The Forecast API is available on the Professional plan and higher. Examples of the data outputted by this stream are available [here](https://weatherstack.com/documentation).

### Features

| Feature                           | Supported? |
| :-------------------------------- | :--------- |
| Full Refresh Sync - (append only) | Yes        |
| Incremental - Append Sync         | Yes        |
| Namespaces                        | No         |

## Getting started

### Requirements

- An Weatherstack API key
- A city or zip code location for which you want to get weather data
- A historical date to enable the api stream to gather data for a specific date

### Setup guide

Visit the [Wetherstack](https://weatherstack.com/) to create a user account and obtain an API key. The current and forecast streams are available with the free plan.

## Rate limiting

The free plan allows 250 calls per month, you won't get beyond these limits with existing Airbyte's sync frequencies.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject         |
| :------ | :--------- | :------------------------------------------------------- | :-------------- |
| 1.1.3 | 2025-02-22 | [54498](https://github.com/airbytehq/airbyte/pull/54498) | Update dependencies |
| 1.1.2 | 2025-02-15 | [47532](https://github.com/airbytehq/airbyte/pull/47532) | Update dependencies |
| 1.1.1 | 2024-08-16 | [44196](https://github.com/airbytehq/airbyte/pull/44196) | Bump source-declarative-manifest version |
| 1.1.0 | 2024-08-14 | [44046](https://github.com/airbytehq/airbyte/pull/44046) | Refactor connector to manifest-only format |
| 1.0.2 | 2024-08-12 | [43892](https://github.com/airbytehq/airbyte/pull/43892) | Update dependencies |
| 1.0.1 | 2024-08-10 | [43615](https://github.com/airbytehq/airbyte/pull/43615) | Update dependencies |
| 1.0.0 | 2024-08-04 | [43298](https://github.com/airbytehq/airbyte/pull/43298) | Migrate to LowCode |
| 0.1.12 | 2024-08-03 | [43177](https://github.com/airbytehq/airbyte/pull/43177) | Update dependencies |
| 0.1.11 | 2024-07-27 | [42672](https://github.com/airbytehq/airbyte/pull/42672) | Update dependencies |
| 0.1.10 | 2024-07-20 | [42280](https://github.com/airbytehq/airbyte/pull/42280) | Update dependencies |
| 0.1.9 | 2024-07-13 | [41887](https://github.com/airbytehq/airbyte/pull/41887) | Update dependencies |
| 0.1.8 | 2024-07-10 | [41566](https://github.com/airbytehq/airbyte/pull/41566) | Update dependencies |
| 0.1.7 | 2024-07-09 | [41241](https://github.com/airbytehq/airbyte/pull/41241) | Update dependencies |
| 0.1.6 | 2024-07-06 | [40876](https://github.com/airbytehq/airbyte/pull/40876) | Update dependencies |
| 0.1.5 | 2024-06-26 | [40549](https://github.com/airbytehq/airbyte/pull/40549) | Migrate off deprecated auth package |
| 0.1.4 | 2024-06-25 | [40414](https://github.com/airbytehq/airbyte/pull/40414) | Update dependencies |
| 0.1.3 | 2024-06-22 | [40086](https://github.com/airbytehq/airbyte/pull/40086) | Update dependencies |
| 0.1.2 | 2024-06-06 | [39190](https://github.com/airbytehq/airbyte/pull/39190) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38438](https://github.com/airbytehq/airbyte/pull/38438) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-09-08 | [16473](https://github.com/airbytehq/airbyte/pull/16473) | Initial release |

</details>
