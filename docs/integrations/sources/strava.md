# Strava

## Overview

The Strava source can sync data from the [Strava API](https://developers.strava.com/)

Useful links:

* [Getting Started with the Strava API](https://developers.strava.com/docs/getting-started/)  
* [Strava API v3 API and SDK Reference](https://developers.strava.com/docs/reference/)
* [Authentication](https://developers.strava.com/docs/authentication/)

#### Output schema

This Source is capable of syncing the following Streams:

* [Athlete Stats](https://developers.strava.com/docs/reference/#api-Athletes-getStats)
* [Activities](https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities) \(Incremental\)

#### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

### Requirements

* client\_id - Strava account client ID
* client\_secret - Strava account client secret
* refresh\_token - Strava account refresh token 
* athlete\_id - Strava athlete ID (only used for [Athlete Stats](https://developers.strava.com/docs/reference/#api-Athletes-getStats))
* query\_start\_timestamp - Starting timestamp for listing activities (only used for [Activities](https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities))

### Setup guide

Follow these steps to get the required credentials and inputs:
* `client_id` and `client_secret`
    * [Create a Strava account](https://developers.strava.com/docs/getting-started/#account)
    * Continue to follow the instructions from the doc above to obtain `client_id` and `client_secret`
* `refresh_token`
    * Enter this URL into your browser (make sure to add your `client_id` from previous step:
        * `http://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=activity:read_all`
    * Authorize through the UI
    * Browser will redirect you to an empty page with a URL similar to `http://localhost/exchange_token?state=&code=b55003496d87a9f0b694ca1680cd5690d27d9d28&scope=activity:read_all`
    * Copy the authorization code above (in this example it would be `b55003496d87a9f0b694ca1680cd5690d27d9d28`)
    * Make a cURL request to exchange the authorization code and scope for a refresh token:
    * ```
      curl -X POST https://www.strava.com/oauth/token \
      -F client_id=YOUR_CLIENT_ID \
      -F client_secret=YOUR_CLIENT_SECRET \
      -F code=AUTHORIZATION_CODE \
      -F grant_type=authorization_code
      ```
    * The resulting json will contain the `refresh_token`
    * Example Result:
    * ```
        {
            "token_type": "Bearer",
            "expires_at": 1562908002,
            "expires_in": 21600,
            "refresh_token": "REFRESHTOKEN",
            "access_token": "ACCESSTOKEN",
            "athlete": {
                "id": 123456,
                "username": "MeowTheCat",
                "resource_state": 2,
                "firstname": "Meow",
                "lastname": "TheCat",
                "city": "",
                "state": "",
                "country": null,
                ...
            }
        }
      ```
    * Refer to Strava's [Getting Started - Oauth](https://developers.strava.com/docs/getting-started/#oauth) or [Authentication](https://developers.strava.com/docs/authentication/) documents for more information
* `athlete_id`
    * Go to your athlete page by clicking your name on the [Strava dashboard](https://www.strava.com/dashboard) or click on "My Profile" on the drop down after hovering on your top bar icon
    * The number at the end of the url will be your `athlete_id`. For example `17831421` would be the `athlete_id` for https://www.strava.com/athletes/17831421

## Performance considerations

Strava API has limitations to 100 requests every 15 minutes, 1000 daily.
More information about Strava rate limits and adjustments to those limits can be found [here](https://developers.strava.com/docs/rate-limits).

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.2 | 2021-12-15 | [8799](https://github.com/airbytehq/airbyte/pull/8799) | Implement OAuth 2.0 support |
| 0.1.1 | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |
| 0.1.0 | 2021-10-18 | [7151](https://github.com/airbytehq/airbyte/pull/7151) | Initial release supporting Strava API |

