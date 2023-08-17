# Breezometer

## Overview

Breezometer connector lets you request environment information like air quality, pollen forecast, current and forecasted weather and wildfires for a specific location.

## Authentication

Breezometer uses a token to authenticate. Every BreezoMeter account is assigned an API Key. The key stores permissions, rate limits, daily quota, API usage, and billing information associated with an account. To send an authenticated API request, you add the API key parameter and include your key to the request URL. For more informations, consult the [documentation](https://docs.breezometer.com/api-documentation/introduction/#authentication).

## Endpoints

- [Air Quality - Current](https://docs.breezometer.com/api-documentation/air-quality-api/v2/#current-conditions)
- [Air Quality - Forecast](https://docs.breezometer.com/api-documentation/air-quality-api/v2/#hourly-forecast)
- [Air Quality - Historical](https://docs.breezometer.com/api-documentation/air-quality-api/v2/#hourly-history)
- [Pollen - Forecast](https://docs.breezometer.com/api-documentation/pollen-api/v2/#daily-forecast)
- [Weather - Current](https://docs.breezometer.com/api-documentation/weather-api/v1/#current-conditions)
- [Weather - Forecast](https://docs.breezometer.com/api-documentation/weather-api/v1/#hourly-forecast)
- [Wildfire - Burnt Area](https://docs.breezometer.com/api-documentation/wildfire-tracker-api/v1/#burnt-area-api)
- [Wildfire - Locate](https://docs.breezometer.com/api-documentation/wildfire-tracker-api/v1/#current-conditions)
