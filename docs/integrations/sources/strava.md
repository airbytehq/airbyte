# Strava

This page guides you through the process of setting up the Strava source connector.

## Prerequisites

- A Strava account for the athlete whose data you want to sync.
- The athlete's numeric Athlete ID. See [Find your Athlete ID](#find-your-athlete-id).
- The `activity:read_all` scope, granted by the athlete during authorization. Strava lets the athlete uncheck requested scopes on the authorization page, and refreshing a token doesn't add missing scopes.
<!-- env:oss -->
- **Airbyte Open Source only:** A Strava API application, which provides the Client ID and Client Secret, and a refresh token for the athlete. Strava requires a subscription to create an API application. New applications start in single-player mode, which means only the account that owns the application can authorize it.
<!-- /env:oss -->

## Setup guide

### Step 1: Set up Strava

#### Find your Athlete ID

1. Sign in to Strava and open your athlete page. Click your name on the [Strava dashboard](https://www.strava.com/dashboard), or hover over your profile icon in the top bar and click **My Profile**.
2. Copy the number at the end of the URL. For example, the Athlete ID for `https://www.strava.com/athletes/17831421` is `17831421`.

The Athlete ID must belong to the same athlete who authorizes the connection. Strava's athlete stats endpoint only returns stats for the authenticated athlete.

<!-- env:oss -->

#### Get API credentials (Airbyte Open Source)

1. Follow Strava's [Getting Started guide](https://developers.strava.com/docs/getting-started/#account) to create an API application at [strava.com/settings/api](https://www.strava.com/settings/api). Set **Authorization Callback Domain** to `localhost`.
2. Copy the **Client ID** and **Client Secret** from the **My API Application** page.
3. Enter the following URL in your browser, replacing `[REPLACE_WITH_YOUR_CLIENT_ID]` with your Client ID:

   ```text
   https://www.strava.com/oauth/authorize?client_id=[REPLACE_WITH_YOUR_CLIENT_ID]&response_type=code&redirect_uri=https://localhost/exchange_token&approval_prompt=force&scope=activity:read_all
   ```

4. Sign in if prompted, keep the requested permission checked, and click **Authorize**.
5. Your browser redirects to a page that doesn't load, with a URL similar to `https://localhost/exchange_token?state=&code=b55003496d87a9f0b694ca1680cd5690d27d9d28&scope=activity:read_all`. Confirm that the `scope` parameter includes `activity:read_all`, then copy the value of the `code` parameter. In this example, the code is `b55003496d87a9f0b694ca1680cd5690d27d9d28`. The code is short-lived and works only once.
6. Exchange the authorization code for a refresh token:

   ```bash
   curl -X POST https://www.strava.com/oauth/token \
     -F client_id=YOUR_CLIENT_ID \
     -F client_secret=YOUR_CLIENT_SECRET \
     -F code=AUTHORIZATION_CODE \
     -F grant_type=authorization_code
   ```

7. Copy the `refresh_token` value from the JSON response. The response looks similar to this:

   ```json
   {
     "token_type": "Bearer",
     "expires_at": 1562908002,
     "expires_in": 21600,
     "refresh_token": "REFRESHTOKEN",
     "access_token": "ACCESSTOKEN",
     "athlete": {
       "id": 123456,
       "username": "MeowTheCat",
       ...
     }
   }
   ```

For more information, see Strava's [Authentication](https://developers.strava.com/docs/authentication/) documentation.

<!-- /env:oss -->

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the source setup page, select **Strava** from the source type list and enter a name for this connector.
4. Click **Authenticate your account**.
5. Sign in to Strava and authorize access. Keep the requested activity permission checked.
6. Enter the **Athlete ID** and **Start Date**.
7. Click **Set up source**.

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Open your local Airbyte instance.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the source setup page, select **Strava** from the source type list and enter a name for this connector.
4. Enter your **Client ID**, **Client Secret**, and **Refresh Token**.
5. Enter the **Athlete ID** and **Start Date**.
6. Click **Set up source**.

<!-- /env:oss -->

**Start Date** is a UTC date and time in the format `YYYY-MM-DDTHH:MM:SSZ`. The connector only syncs activities that start after this date. It doesn't filter the Athlete Stats stream.

The connection check reads both athlete stats and activities, so setup fails if the token is missing the `activity:read_all` scope.

## Supported sync modes

The Strava source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

## Supported streams

| Stream | Endpoint | Incremental | Notes |
| :----- | :------- | :---------- | :---- |
| Athlete Stats | [Get Athlete Stats](https://developers.strava.com/docs/reference/#api-Athletes-getStats) | No | Returns one record of cumulative ride, run, and swim totals. Strava only includes activities with **Everyone** visibility in these totals. |
| Activities | [List Athlete Activities](https://developers.strava.com/docs/reference/#api-Activities-getLoggedInAthleteActivities) | Yes | Uses `start_date` as the cursor and `id` as the primary key. Includes activities with **Only You** visibility because the connector requires `activity:read_all`. |

## Authentication and token refresh

Strava access tokens expire after six hours. Airbyte refreshes them automatically and saves the latest refresh token in the source configuration. Strava invalidates a refresh token as soon as it issues a new one, so if you exchange tokens outside Airbyte, use the latest refresh token when you update the source.

## Troubleshooting

- **Token refresh fails with a configuration error:** If Strava rejects the refresh request with `Bad Request` or `Authorization Error`, the refresh token, Client ID, or Client Secret is invalid or has been revoked. Retrying the sync won't fix this. In Airbyte Cloud, re-authenticate the source. In Airbyte Open Source, generate a new refresh token or update the Client ID and Client Secret, then update the source.
- **`activity:read_permission` error:** The token doesn't have the `activity:read_all` scope. Reauthorize with `activity:read_all`, make sure the athlete keeps the permission checked, and update the source credentials.
- **`Application` / `Status` / `Inactive` error:** The Strava API application is inactive. Restore its access with Strava before retrying. Changing the Athlete ID or Start Date doesn't resolve this error.

## Performance considerations

Strava limits API usage per application. By default, read requests are limited to 100 requests every 15 minutes and 1,000 requests per day. The 15-minute limit resets at 0, 15, 30, and 45 minutes past the hour, and the daily limit resets at midnight UTC. Requests over the limit return HTTP `429 Too Many Requests`.

The Activities stream requests 30 activities per page, and each page is one request. Syncing a long activity history from an early start date uses more requests. For details and information about limit increases, see Strava's [Rate Limits](https://developers.strava.com/docs/rate-limits) documentation.

## IP allow list

If you use Airbyte Cloud and your organization restricts access to specific IPs, add the [Airbyte Cloud IP addresses](https://docs.airbyte.com/platform/operating-airbyte/ip-allowlist) to your allow list.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date | Pull Request | Subject |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.4.1 | 2026-10-15 | [88994](https://github.com/airbytehq/airbyte/pull/88994) | Show a re-authenticate error when Strava rejects the refresh token or app credentials, and stop sending an unused scopes parameter on token refresh. |
| 0.4.0 | 2026-10-09 | [88212](https://github.com/airbytehq/airbyte/pull/88212) | Fix OAuth token expiry and refresh-token rotation; validate activity permissions during setup. See the [migration guide](strava-migrations.md). |
| 0.3.52 | 2026-06-30 | [81265](https://github.com/airbytehq/airbyte/pull/81265) | Update dependencies |
| 0.3.51 | 2026-06-23 | [80672](https://github.com/airbytehq/airbyte/pull/80672) | Update dependencies |
| 0.3.50 | 2026-06-16 | [80056](https://github.com/airbytehq/airbyte/pull/80056) | Update dependencies |
| 0.3.49 | 2026-06-09 | [79524](https://github.com/airbytehq/airbyte/pull/79524) | Update dependencies |
| 0.3.48 | 2026-06-02 | [78990](https://github.com/airbytehq/airbyte/pull/78990) | Update dependencies |
| 0.3.47 | 2026-04-28 | [77413](https://github.com/airbytehq/airbyte/pull/77413) | Update dependencies |
| 0.3.46 | 2026-04-21 | [76782](https://github.com/airbytehq/airbyte/pull/76782) | Update dependencies |
| 0.3.45 | 2026-03-31 | [75863](https://github.com/airbytehq/airbyte/pull/75863) | Update dependencies |
| 0.3.44 | 2026-03-17 | [75088](https://github.com/airbytehq/airbyte/pull/75088) | Update dependencies |
| 0.3.43 | 2026-03-10 | [74577](https://github.com/airbytehq/airbyte/pull/74577) | Update dependencies |
| 0.3.42 | 2026-03-03 | [73975](https://github.com/airbytehq/airbyte/pull/73975) | Update dependencies |
| 0.3.41 | 2026-02-03 | [72765](https://github.com/airbytehq/airbyte/pull/72765) | Update dependencies |
| 0.3.40 | 2026-01-20 | [72132](https://github.com/airbytehq/airbyte/pull/72132) | Update dependencies |
| 0.3.39 | 2026-01-14 | [71619](https://github.com/airbytehq/airbyte/pull/71619) | Update dependencies |
| 0.3.38 | 2025-12-18 | [70608](https://github.com/airbytehq/airbyte/pull/70608) | Update dependencies |
| 0.3.37 | 2025-11-25 | [70057](https://github.com/airbytehq/airbyte/pull/70057) | Update dependencies |
| 0.3.36 | 2025-11-18 | [69586](https://github.com/airbytehq/airbyte/pull/69586) | Update dependencies |
| 0.3.35 | 2025-10-29 | [68991](https://github.com/airbytehq/airbyte/pull/68991) | Update dependencies |
| 0.3.34 | 2025-10-21 | [68515](https://github.com/airbytehq/airbyte/pull/68515) | Update dependencies |
| 0.3.33 | 2025-10-14 | [67918](https://github.com/airbytehq/airbyte/pull/67918) | Update dependencies |
| 0.3.32 | 2025-10-07 | [67456](https://github.com/airbytehq/airbyte/pull/67456) | Update dependencies |
| 0.3.31 | 2025-09-30 | [66893](https://github.com/airbytehq/airbyte/pull/66893) | Update dependencies |
| 0.3.30 | 2025-09-23 | [66371](https://github.com/airbytehq/airbyte/pull/66371) | Update dependencies |
| 0.3.29 | 2025-09-09 | [65664](https://github.com/airbytehq/airbyte/pull/65664) | Update dependencies |
| 0.3.28 | 2025-08-24 | [65412](https://github.com/airbytehq/airbyte/pull/65412) | Update dependencies |
| 0.3.27 | 2025-08-16 | [65038](https://github.com/airbytehq/airbyte/pull/65038) | Update dependencies |
| 0.3.26 | 2025-08-02 | [64020](https://github.com/airbytehq/airbyte/pull/64020) | Update dependencies |
| 0.3.25 | 2025-07-12 | [63084](https://github.com/airbytehq/airbyte/pull/63084) | Update dependencies |
| 0.3.24 | 2025-07-05 | [62682](https://github.com/airbytehq/airbyte/pull/62682) | Update dependencies |
| 0.3.23 | 2025-06-28 | [62278](https://github.com/airbytehq/airbyte/pull/62278) | Update dependencies |
| 0.3.22 | 2025-06-14 | [61608](https://github.com/airbytehq/airbyte/pull/61608) | Update dependencies |
| 0.3.21 | 2025-05-25 | [60208](https://github.com/airbytehq/airbyte/pull/60208) | Update dependencies |
| 0.3.20 | 2025-05-04 | [59581](https://github.com/airbytehq/airbyte/pull/59581) | Update dependencies |
| 0.3.19 | 2025-04-27 | [59034](https://github.com/airbytehq/airbyte/pull/59034) | Update dependencies |
| 0.3.18 | 2025-04-19 | [58385](https://github.com/airbytehq/airbyte/pull/58385) | Update dependencies |
| 0.3.17 | 2025-04-12 | [57939](https://github.com/airbytehq/airbyte/pull/57939) | Update dependencies |
| 0.3.16 | 2025-04-05 | [57411](https://github.com/airbytehq/airbyte/pull/57411) | Update dependencies |
| 0.3.15 | 2025-03-29 | [56879](https://github.com/airbytehq/airbyte/pull/56879) | Update dependencies |
| 0.3.14 | 2025-03-22 | [56280](https://github.com/airbytehq/airbyte/pull/56280) | Update dependencies |
| 0.3.13 | 2025-03-08 | [55588](https://github.com/airbytehq/airbyte/pull/55588) | Update dependencies |
| 0.3.12 | 2025-03-01 | [55095](https://github.com/airbytehq/airbyte/pull/55095) | Update dependencies |
| 0.3.11 | 2025-02-22 | [54482](https://github.com/airbytehq/airbyte/pull/54482) | Update dependencies |
| 0.3.10 | 2025-02-15 | [54087](https://github.com/airbytehq/airbyte/pull/54087) | Update dependencies |
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
