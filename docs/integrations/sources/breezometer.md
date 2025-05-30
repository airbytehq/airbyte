# Breezometer

Breezometer connector lets you request environment information like air quality, pollen forecast, current and forecasted weather and wildfires for a specific location.

## Prerequisites

- A Breezometer
- An `api_key`, that can be found on your Breezometer account home page.

## Supported sync modes

The Breezometer connector supports full sync refresh.

## Airbyte Open Source

- API Key
- Latitude
- Longitude
- Days to Forecast
- Hours to Forecast
- Historic Hours
- Radius

## Supported Streams

- [Air Quality - Current](https://docs.breezometer.com/api-documentation/air-quality-api/v2/#current-conditions)
- [Air Quality - Forecast](https://docs.breezometer.com/api-documentation/air-quality-api/v2/#hourly-forecast)
- [Air Quality - Historical](https://docs.breezometer.com/api-documentation/air-quality-api/v2/#hourly-history)
- [Pollen - Forecast](https://docs.breezometer.com/api-documentation/pollen-api/v2/#daily-forecast)
- [Weather - Current](https://docs.breezometer.com/api-documentation/weather-api/v1/#current-conditions)
- [Weather - Forecast](https://docs.breezometer.com/api-documentation/weather-api/v1/#hourly-forecast)
- [Wildfire - Burnt Area](https://docs.breezometer.com/api-documentation/wildfire-tracker-api/v1/#burnt-area-api)
- [Wildfire - Locate](https://docs.breezometer.com/api-documentation/wildfire-tracker-api/v1/#current-conditions)

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                     |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------ |
| 0.2.0   | 2024-08-22 | [44563](https://github.com/airbytehq/airbyte/pull/44563) | Refactor connector to manifest-only format  |
| 0.1.1   | 2024-05-21 | [38529](https://github.com/airbytehq/airbyte/pull/38529) | [autopull] base image + poetry + up_to_date |
| 0.1.0   | 2022-10-29 | [18650](https://github.com/airbytehq/airbyte/pull/18650) | Initial version/release of the connector.   |

</details>
