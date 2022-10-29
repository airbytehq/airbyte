# Breezometer Air Quality 

Breezometer Air Quality connector returns hourly air-quality forecasts for the specified location. Each forecast includes hourly air quality indexes, pollutant data, and health recommendations for a maximum of 96 hours (4 days).

## Prerequisites
* A Breezometer
* An `api_key`, that can be found on your Breezometer account home page.

## Supported sync modes

The Breezometer Air Quality connector supports full sync refresh.

## Airbyte Open Source

* API Key
* Latitude
* Longitude
* Number of hours to forecast. Is a number between 1 and 96.

## Supported Streams

There is only one endpoint, that responds with air quality information for the given location.


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.0   | 2022-10-29 | [18049](https://github.com/airbytehq/airbyte/pull/18652) | Initial version/release of the connector.