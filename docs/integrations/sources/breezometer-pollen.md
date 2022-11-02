# Breezometer

Breezometer connector lets you request pollen information including types, plants, and indexes for a specific location.

## Prerequisites
* A Breezometer
* An `api_key`, that can be found on your Breezometer account home page.

## Supported sync modes

The Breezometer connector supports full sync refresh.

## Airbyte Open Source

* API Key
* Latitude
* Longitude
* Number of days to forecast. Is a number between 1 and 5.

## Supported Streams

There is only one endpoint, that responds with information for various trees and grass conditions in the given location.


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.1.0   | 2022-10-29 | [18650](https://github.com/airbytehq/airbyte/pull/18650) | Initial version/release of the connector.