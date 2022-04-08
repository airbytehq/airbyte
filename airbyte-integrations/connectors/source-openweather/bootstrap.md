# OpenWeather
OpenWeather is an online service offering an API to retrieve historical, current and forecasted weather data over the globe.

## One Call API
The *One Call API* enable retrieval of multiple weather data for a location in a single call. 
I made this stream implementation a priority because it has a free plan that might be valuable for all data teams building models around weather data.
The API returns current weather data along with other time resolutions (minutely, hourly, daily) and weather alerts.

### Full refresh vs incremental stream implementation
I did not implement a full refresh stream because One Call API calls are not idempotent: two subsequents calls with the same parameters might give different results. Moreover, it has no historical capabilities (there is a specific historical API for that) and only gives current weather conditions and forecasts. It's why I implemented an incremental stream without a feature to request past data.

### Auth
API calls are authenticated through an API key passed in a query string parameter (`appid`). API keys can be generated from OpenWeather's user account panel.

### Rate limits
The API does have some rate limiting logic but it's not very transparent to the user. There is no endpoint to check calls consumption. It is stated that the free plan allows 60 calls / minute or 1,000,000 calls/month. If the limit is exceeded the user account (not only the API key) gets blocked for an unknown duration.