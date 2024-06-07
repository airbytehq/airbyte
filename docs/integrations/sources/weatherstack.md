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
| 0.1.2 | 2024-06-06 | [39190](https://github.com/airbytehq/airbyte/pull/39190) | [autopull] Upgrade base image to v1.2.2 |
| 0.1.1 | 2024-05-20 | [38438](https://github.com/airbytehq/airbyte/pull/38438) | [autopull] base image + poetry + up_to_date |
| 0.1.0 | 2022-09-08 | [16473](https://github.com/airbytehq/airbyte/pull/16473) | Initial release |

</details>
