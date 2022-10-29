# Breezometer Air Quality

## Overview

Breezometer Air Quality connector returns hourly air-quality forecasts for the specified location. Each forecast includes hourly air quality indexes, pollutant data, and health recommendations for a maximum of 96 hours (4 days).

## Authentication

Breezometer Air Quality API uses a token to authenticate. Every BreezoMeter account is assigned an API Key. The key stores permissions, rate limits, daily quota, API usage, and billing information associated with an account. To send an authenticated API request, you add the API key parameter and include your key to the request URL. For more informations, consult the [documentation](https://docs.breezometer.com/api-documentation/introduction/#authentication).

## Endpoints

There is only one endpoint, that responds with air quality information for the given location.
