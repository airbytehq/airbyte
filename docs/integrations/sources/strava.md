# Strava

This page guides you through the process of setting up the Strava source connector.

## Prerequisites

Scopes:

- `activity:read_all`

## Setup guide

### Step 1: Set up Strava

<!-- env:oss -->

**For Airbyte Open Source:**

Follow these steps to get the required credentials and inputs:

- `client_id` and `client_secret`
  - [Create a Strava account](https://developers.strava.com/docs/getting-started/#account)
  - Continue to follow the instructions from the doc above to obtain `client_id` and `client_secret`
- `refresh_token`
  - Enter this URL into your browser (make sure to add your `client_id` from previous step:
    - `https://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=https://localhost/exchange_token&approval_prompt=force&scope=activity:read_all`
  - Authorize through the UI
  - Browser will redirect you to an empty page with a URL similar to `https://localhost/exchange_token?state=&code=b55003496d87a9f0b694ca1680cd5690d27d9d28&scope=activity:read_all`
  - Copy the authorization code above (in this example it would be `b55003496d87a9f0b694ca1680cd5690d27d9d28`)
  - Make a cURL request to exchange the authorization code and scope for a refresh token:
  - ```
    curl -X POST https://www.strava.com/oauth/token \
    -F client_id=YOUR_CLIENT_ID \
    -F client_secret=YOUR_CLIENT_SECRET \
    -F code=AUTHORIZATION_CODE \
    -F grant_type=authorization_code
    ```
  - The resulting json will contain the `refresh_token`
  - Example Result:
  - ```
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
  - Refer to Strava's [Getting Started - Oauth](https://developers.strava.com/docs/getting-started/#oauth) or [Authentication](https://developers.strava.com/docs/authentication/) documents for more information
- `athlete_id`
  - Go to your athlete page by clicking your name on the [Strava dashboard](https://www.strava.com/dashboard) or click on "My Profile" on the drop down after hovering on your top bar icon
  - The number at the end of the url will be your `athlete_id`. For example `17831421` would be the `athlete_id` for https://www.strava.com/athletes/17831421

<!-- /env:oss -->

<!-- env:cloud -->

**For Airbyte Cloud:**

- `athlete_id`
  - Go to your athlete page by clicking your name on the [Strava dashboard](https://www.strava.com/dashboard) or click on "My Profile" on the drop down after hovering on your top bar icon
  - The number at the end of the url will be your `athlete_id`. For example `17831421` would be the `athlete_id` for https://www.strava.com/athletes/17831421

<!-- /env:cloud -->

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Strava** from the Source type dropdown and enter a name for this connector.
4. lick `Authenticate your account`.
5. Log in and Authorize to the Strava account
6. Set required **Athlete ID** and **Start Date**
7. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Strava** from the Source type dropdown and enter a name for this connector.
4. Add **Client ID**, **Client Secret** and **Refresh Token**
5. Set required **Athlete ID** and **Start Date**
6. Click `Set up source`.
<!-- /env:oss -->

## Supported sync modes

The Strava source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

- [Athlete Stats](https://developers.strava.com/docs/reference/#api-Athletes-getStats)
- [Activities](https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities) \(Incremental\)

## Performance considerations

Strava API has limitations to 100 requests every 15 minutes, 1000 daily.
More information about Strava rate limits and adjustments to those limits can be found [here](https://developers.strava.com/docs/rate-limits).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.3.9 | 2025-02-08 | [53562](https://github.com/airbytehq/airbyte/pull/53562) | Update dependencies |
| 0.3.8 | 2025-02-01 | [53075](https://github.com/airbytehq/airbyte/pull/53075) | Update dependencies |
| 0.3.7 | 2025-01-25 | [52019](https://github.com/airbytehq/airbyte/pull/52019) | Update dependencies |
| 0.3.6 | 2025-01-11 | [51460](https://github.com/airbytehq/airbyte/pull/51460) | Update dependencies |
| 0.3.5 | 2024-12-28 | [50764](https://github.com/airbytehq/airbyte/pull/50764) | Update dependencies |
| 0.3.4 | 2024-12-21 | [50337](https://github.com/airbytehq/airbyte/pull/50337) | Update dependencies |
| 0.3.3 | 2024-12-14 | [49777](https://github.com/airbytehq/airbyte/pull/49777) | Update dependencies |
| 0.3.2 | 2024-12-12 | [49432](https://github.com/airbytehq/airbyte/pull/49432) | Update dependencies |
| 0.3.1 | 2024-10-28 | [47601](https://github.com/airbytehq/airbyte/pull/47601) | Update dependencies |
| 0.3.0 | 2024-08-27 | [44820](https://github.com/airbytehq/airbyte/pull/44820) | Refactor connector to manifest-only format |
| 0.2.17 | 2024-08-24 | [44667](https://github.com/airbytehq/airbyte/pull/44667) | Update dependencies |
| 0.2.16 | 2024-08-17 | [44354](https://github.com/airbytehq/airbyte/pull/44354) | Update dependencies |
| 0.2.15 | 2024-08-10 | [43588](https://github.com/airbytehq/airbyte/pull/43588) | Update dependencies |
| 0.2.14 | 2024-08-03 | [43283](https://github.com/airbytehq/airbyte/pull/43283) | Update dependencies |
| 0.2.13 | 2024-07-20 | [42131](https://github.com/airbytehq/airbyte/pull/42131) | Fix bug in start date format in manifest |
| 0.2.12 | 2024-07-20 | [42353](https://github.com/airbytehq/airbyte/pull/42353) | Update dependencies |
| 0.2.11 | 2024-07-13 | [41933](https://github.com/airbytehq/airbyte/pull/41933) | Update dependencies |
| 0.2.10 | 2024-07-10 | [41499](https://github.com/airbytehq/airbyte/pull/41499) | Update dependencies |
| 0.2.9 | 2024-07-09 | [41201](https://github.com/airbytehq/airbyte/pull/41201) | Update dependencies |
| 0.2.8 | 2024-07-06 | [40970](https://github.com/airbytehq/airbyte/pull/40970) | Update dependencies |
| 0.2.7 | 2024-06-25 | [40393](https://github.com/airbytehq/airbyte/pull/40393) | Update dependencies |
| 0.2.6 | 2024-06-21 | [39941](https://github.com/airbytehq/airbyte/pull/39941) | Update dependencies |
| 0.2.5 | 2024-06-06 | [39221](https://github.com/airbytehq/airbyte/pull/39221) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.4 | 2024-04-19 | [37266](https://github.com/airbytehq/airbyte/pull/37266) | Updating to 0.80.0 CDK |
| 0.2.3 | 2024-04-18 | [37266](https://github.com/airbytehq/airbyte/pull/37266) | Manage dependencies with Poetry. |
| 0.2.2 | 2024-04-15 | [37266](https://github.com/airbytehq/airbyte/pull/37266) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1 | 2024-04-12 | [37266](https://github.com/airbytehq/airbyte/pull/37266) | schema descriptions |
| 0.2.0 | 2023-10-24 | [31007](https://github.com/airbytehq/airbyte/pull/31007) | Migrate to low-code framework |
| 0.1.4 | 2023-03-23 | [24368](https://github.com/airbytehq/airbyte/pull/24368) | Add date-time format for input |
| 0.1.3 | 2023-03-15 | [24101](https://github.com/airbytehq/airbyte/pull/24101) | certified to beta, fixed spec, fixed SAT, added unit tests |
| 0.1.2 | 2021-12-15 | [8799](https://github.com/airbytehq/airbyte/pull/8799) | Implement OAuth 2.0 support |
| 0.1.1 | 2021-12-06 | [8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |
| 0.1.0 | 2021-10-18 | [7151](https://github.com/airbytehq/airbyte/pull/7151) | Initial release supporting Strava API |

</details>
