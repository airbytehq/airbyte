# OpenWeather

## Overview

This source connector syncs data from the [OpenWeather One Call API](https://openweathermap.org/api/one-call-api). This API allows to obtain current and weather data from a geolocation expressed in latitude and longitude.

### Output schema

This source currently has a single stream, `openweather_one_call`. An example of the data outputted by this stream is available [here](https://openweathermap.org/api/one-call-api#example).

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync - (append only) | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

## Getting started

### Requirements

* An OpenWeather API key
* Latitude and longitude of the location for which you want to get weather data

### Setup guide

Visit the [OpenWeather](https://openweathermap.org) to create a user account and obtain an API key. The *One Call API* is available with the free plan.

## Rate limiting
The free plan allows 60 calls per minute and 1,000,000 calls per month, you won't get beyond these limits with existing Airbyte's sync frequencies.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.6 | 2022-06-21 | [16136](https://github.com/airbytehq/airbyte/pull/16136) | Update openweather onecall api to 3.0. |
| 0.1.5 | 2022-06-21 | [13864](https://github.com/airbytehq/airbyte/pull/13864) | No changes. Used connector to test publish workflow changes. |
| 0.1.4 | 2022-04-27 | [12397](https://github.com/airbytehq/airbyte/pull/12397) | No changes. Used connector to test publish workflow changes. |
| 0.1.0 | 2021-10-27 | [7434](https://github.com/airbytehq/airbyte/pull/7434) | Initial release |

