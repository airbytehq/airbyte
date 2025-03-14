# Snapchat Marketing

This page guides you through the process of setting up the [Snapchat Marketing](https://marketingapi.snapchat.com/docs/) source connector.

## Prerequisites

<!-- env:cloud -->

**For Airbyte Cloud:**

- An existing Snapchat Marketing business account
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

- Client ID
- Client Secret
- Refresh Token

<!-- /env:oss -->

## Setup guide

### Step 1: Set up Snapchat

1. [Set up a Snapchat Business account](https://businesshelp.snapchat.com/s/article/get-started?language=en_US)

<!-- env:oss -->

**For Airbyte Open Source:**

2. [Activate Access to the Snapchat Marketing API](https://businesshelp.snapchat.com/s/article/api-apply?language=en_US)
3. Add the OAuth2 app:
   - Adding the OAuth2 app requires the `redirect_url` parameter.
     - If you have the API endpoint that will handle next OAuth process, write it to this parameter.
     - If you do not have the API endpoint, simply use a valid URL.Refer to the discussion here for more information: [Snapchat Redirect URL - Clarity in documentation please](https://github.com/Snap-Kit/bitmoji-sample/issues/3)
   - Save the **Client ID** and **Client Secret**
4. Obtain a refresh token using OAuth2 authentication workflow.
   - Open the authorize link in a browser. It will look similar to this:
   ```
   https://accounts.snapchat.com/login/oauth2/authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&scope=snapchat-marketing-api&state=wmKkg0TWgppW8PTBZ20sldUwerf-m
   ```
   - Login & Authorize via UI
   - Locate the `code` query parameter in the redirect
   - Exchange the `code` for an access token and refresh token.

   Your request will appear similar to the following:

   ```text
      curl -X POST \
      -d "code={one_time_use_code}" \
      -d "client_id={client_id}" \
      -d "client_secret={client_secret}"  \
      -d "grant_type=authorization_code"  \
      -d "redirect_uri=redirect_uri"
      https://accounts.snapchat.com/login/oauth2/access_token`
   ```

For more information on authenticating into the Snapchat API, read their documentation [here](https://marketingapi.snapchat.com/docs/#authentication)
   You will receive the API key and refresh token in the response. Use this refresh token for the connector.
   <!-- /env:oss -->

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Snapchat Marketing** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your account`.
5. In the authentication window, log in and authorize access to your Snapchat account
6. (Optional) Choose a Start Date. All data created on or after this date will be synced. If left blank, all records will be synced.

:::tip
The `Start Date` is required for the all streams that use `start_time` as a key (see Supported Streams section below).
:::
7. (Optional) Choose an End Date. All data created on or before this date will be synced. If left blank, all records will be synced.
8. (Optional) Choose the `Action Report Time`, which specifies how conversions are reported. The default is set to `conversion`, and can be modified to `impression`.
9. (Optional) Choose the 'Swip Up Attribution Window', which specifies the length of the attribution window for swipe up actions. The default is 28 days and can be adjusted.
10. (Optional) Choose the `View Attribution Window`, which specifies the length of the attribution window for views. The default is 28 days and can be adjusted.
11. Click 'Set up source'
<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

1. Open the Airbyte UI.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Snapchat Marketing** from the Source type dropdown and enter a name for this connector.
4. Add the **Client ID**, **Client Secret**, and **Refresh Token** obtained from the setup.
5. (Optional) Choose a Start Date. All data created on or after this date will be synced. If left blank, all records will be synced.

:::tip
The `Start Date` is required for the all streams that use `start_time` as a key (see Supported Streams section below).
:::
6. (Optional) Choose an End Date. All data created on or before this date will be synced.
7. (Optional) Choose the `Action Report Time`, which specifies how conversions are reported. The default is set to `conversion`, and can be modified to `impression`.
8. (Optional) Choose the 'Swip Up Attribution Window', which specifies the length of the attribution window for swipe up actions. The default is 28 days and can be adjusted.
9. (Optional) Choose the `View Attribution Window`, which specifies the length of the attribution window for views. The default is 28 days and can be adjusted.
10. Click 'Set up source'
<!-- /env:oss -->

## Supported streams and sync modes

| Stream                  | Incremental | Key                                 |
|:------------------------|:------------|-------------------------------------|
| AdAccounts              | Yes         | "id"                                |
| Ads                     | Yes         | "id"                                |
| AdSquads                | Yes         | "id"                                |
| Campaigns               | Yes         | "id"                                |
| Creatives               | Yes         | "id"                                |
| Media                   | Yes         | "id"                                |
| Organizations           | Yes         | "id"                                |
| Segments                | Yes         | "id"                                |
| AdAccounts_Stats_Hourly   | Yes         | ["id", "granularity", "start_time"] |
| AdAccounts_Stats_Daily    | Yes         | ["id", "granularity", "start_time"] |
| AdAccounts_Stats_Lifetime | No          | ["id", "granularity"]               |
| Ads_Stats_Hourly          | Yes         | ["id", "granularity", "start_time"] |
| Ads_Stats_Daily           | Yes         | ["id", "granularity", "start_time"] |
| Ads_Stats_Lifetime        | No          | ["id", "granularity"]               |
| AdSquads_Stats_Hourly     | Yes         | ["id", "granularity", "start_time"] |
| AdSquads_Stats_Daily      | Yes         | ["id", "granularity", "start_time"] |
| AdSquads_Stats_Lifetime   | No          | ["id", "granularity"]               |
| Campaigns_Stats_Hourly    | Yes         | ["id", "granularity", "start_time"] |
| Campaigns_Stats_Daily     | Yes         | ["id", "granularity", "start_time"] |
| Campaigns_Stats_Lifetime  | No          | ["id", "granularity"]               |

## Performance considerations

The Snapchat Marketing API limits requests to 1,000 items per page.

Syncing data with an hourly granularity often generates large data volumes and can take longer times to sync. We recommend syncing at a day granularity.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                        |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------|
| 1.5.4 | 2025-03-08 | [55595](https://github.com/airbytehq/airbyte/pull/55595) | Update dependencies |
| 1.5.3 | 2025-03-01 | [54546](https://github.com/airbytehq/airbyte/pull/54546) | Update dependencies |
| 1.5.2 | 2025-02-15 | [54091](https://github.com/airbytehq/airbyte/pull/54091) | Update dependencies |
| 1.5.1 | 2025-02-08 | [53569](https://github.com/airbytehq/airbyte/pull/53569) | Update dependencies |
| 1.5.0 | 2024-11-26 | [44170](https://github.com/airbytehq/airbyte/pull/44170) | Added Optional filters - Organization & Ad Account IDs |
| 1.4.2 | 2025-02-01 | [53083](https://github.com/airbytehq/airbyte/pull/53083) | Update dependencies |
| 1.4.1 | 2025-01-25 | [52403](https://github.com/airbytehq/airbyte/pull/52403) | Update dependencies |
| 1.4.0 | 2025-01-23 | [52110](https://github.com/airbytehq/airbyte/pull/52110) | Make incremental per-partition streams concurrent |
| 1.3.7 | 2025-01-18 | [51999](https://github.com/airbytehq/airbyte/pull/51999) | Update dependencies |
| 1.3.6 | 2025-01-11 | [51431](https://github.com/airbytehq/airbyte/pull/51431) | Update dependencies |
| 1.3.5 | 2024-12-28 | [50796](https://github.com/airbytehq/airbyte/pull/50796) | Update dependencies |
| 1.3.4 | 2024-12-21 | [50308](https://github.com/airbytehq/airbyte/pull/50308) | Update dependencies |
| 1.3.3 | 2024-12-14 | [49414](https://github.com/airbytehq/airbyte/pull/49414) | Update dependencies |
| 1.3.2 | 2024-11-05 | [48375](https://github.com/airbytehq/airbyte/pull/48375) | Re-implement advanced_auth in connector spec |
| 1.3.1 | 2024-10-29 | [47837](https://github.com/airbytehq/airbyte/pull/47837) | Update dependencies |
| 1.3.0 | 2024-10-15 | [46927](https://github.com/airbytehq/airbyte/pull/46927) | Promoting release candidate 1.3.0-rc.1 to a main version. |
| 1.3.0-rc.1  | 2024-10-08 | [46570](https://github.com/airbytehq/airbyte/pull/46570) | Migrate to Manifest-only |
| 1.2.12 | 2024-10-12 | [46800](https://github.com/airbytehq/airbyte/pull/46800) | Update dependencies |
| 1.2.11 | 2024-10-05 | [46419](https://github.com/airbytehq/airbyte/pull/46419) | Update dependencies |
| 1.2.10 | 2024-09-28 | [46106](https://github.com/airbytehq/airbyte/pull/46106) | Update dependencies |
| 1.2.9 | 2024-09-21 | [45780](https://github.com/airbytehq/airbyte/pull/45780) | Update dependencies |
| 1.2.8 | 2024-09-14 | [45477](https://github.com/airbytehq/airbyte/pull/45477) | Update dependencies |
| 1.2.7 | 2024-09-07 | [45278](https://github.com/airbytehq/airbyte/pull/45278) | Update dependencies |
| 1.2.6 | 2024-08-31 | [44998](https://github.com/airbytehq/airbyte/pull/44998) | Update dependencies |
| 1.2.5 | 2024-08-24 | [44735](https://github.com/airbytehq/airbyte/pull/44735) | Update dependencies |
| 1.2.4 | 2024-08-17 | [43859](https://github.com/airbytehq/airbyte/pull/43859) | Update dependencies |
| 1.2.3 | 2024-08-12 | [43826](https://github.com/airbytehq/airbyte/pull/43826) | Fixed the bug with the missing `spend` field to supported `*_stats_*` streams |
| 1.2.2 | 2024-08-10 | [43539](https://github.com/airbytehq/airbyte/pull/43539) | Update dependencies |
| 1.2.1 | 2024-08-03 | [43174](https://github.com/airbytehq/airbyte/pull/43174) | Update dependencies |
| 1.2.0 | 2024-07-31 | [42010](https://github.com/airbytehq/airbyte/pull/42010) | Migrate to CDK v4.1.0 |
| 1.1.2 | 2024-07-27 | [42680](https://github.com/airbytehq/airbyte/pull/42680) | Update dependencies |
| 1.1.1 | 2024-07-20 | [42366](https://github.com/airbytehq/airbyte/pull/42366) | Update dependencies |
| 1.1.0 | 2024-07-16 | [42009](https://github.com/airbytehq/airbyte/pull/42009) | Migrate to CDK v2.4.0 |
| 1.0.3 | 2024-07-13 | [41855](https://github.com/airbytehq/airbyte/pull/41855) | Update dependencies |
| 1.0.2 | 2024-07-10 | [41547](https://github.com/airbytehq/airbyte/pull/41547) | Update dependencies |
| 1.0.1 | 2024-07-09 | [40132](https://github.com/airbytehq/airbyte/pull/40132) | Update dependencies |
| 1.0.0 | 2024-06-20 | [39507](https://github.com/airbytehq/airbyte/pull/39507) | Migrate to low-code CDK and add incremental functionality to `organizations` |
| 0.6.2 | 2024-05-22 | [38574](https://github.com/airbytehq/airbyte/pull/38574) | Update authenticator package |
| 0.6.1 | 2024-04-24 | [36662](https://github.com/airbytehq/airbyte/pull/36662) | Schema descriptions |
| 0.6.0 | 2024-04-10 | [30586](https://github.com/airbytehq/airbyte/pull/30586) | Add `attribution_windows`,`action_report_time` as optional configurable params |
| 0.5.0 | 2024-03-19 | [36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0` |
| 0.4.0 | 2024-02-27 | [35660](https://github.com/airbytehq/airbyte/pull/35660) | Add new fields to streams `ads`, `adsquads`, `creatives`, and `media` |
| 0.3.2 | 2024-02-12 | [35171](https://github.com/airbytehq/airbyte/pull/35171) | Manage dependencies with Poetry. |
| 0.3.0 | 2023-05-22 | [26358](https://github.com/airbytehq/airbyte/pull/26358) | Remove deprecated authSpecification in favour of advancedAuth |
| 0.2.0 | 2023-05-10 | [25948](https://github.com/airbytehq/airbyte/pull/25948) | Introduce new field in the `Campaigns` stream schema |
| 0.1.16 | 2023-04-20 | [20897](https://github.com/airbytehq/airbyte/pull/20897) | Add missing fields to Basic Stats schema |
| 0.1.15 | 2023-03-02 | [22869](https://github.com/airbytehq/airbyte/pull/22869) | Specified date formatting in specification |
| 0.1.14 | 2023-02-10 | [22808](https://github.com/airbytehq/airbyte/pull/22808) | Enable default `AvailabilityStrategy` |
| 0.1.13 | 2023-01-27 | [22023](https://github.com/airbytehq/airbyte/pull/22023) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.12 | 2023-01-11 | [21267](https://github.com/airbytehq/airbyte/pull/21267) | Fix parse empty error response |
| 0.1.11 | 2022-12-23 | [20865](https://github.com/airbytehq/airbyte/pull/20865) | Handle 403 permission error |
| 0.1.10 | 2022-12-15 | [20537](https://github.com/airbytehq/airbyte/pull/20537) | Run on CDK 0.15.0 |
| 0.1.9 | 2022-12-14 | [20498](https://github.com/airbytehq/airbyte/pull/20498) | Fix output state when no records are read |
| 0.1.8 | 2022-10-05 | [17596](https://github.com/airbytehq/airbyte/pull/17596) | Retry 429 and 5xx errors when refreshing access token |
| 0.1.6 | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from specs |
| 0.1.5 | 2022-07-13 | [14577](https://github.com/airbytehq/airbyte/pull/14577) | Added stats streams hourly, daily, lifetime |
| 0.1.4 | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8429) | Update titles and descriptions |
| 0.1.3 | 2021-11-10 | [7811](https://github.com/airbytehq/airbyte/pull/7811) | Add oauth2.0, fix stream_state |
| 0.1.2 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.1 | 2021-07-29 | [5072](https://github.com/airbytehq/airbyte/pull/5072) | Fix bug with incorrect stream_state value |
| 0.1.0 | 2021-07-26 | [4843](https://github.com/airbytehq/airbyte/pull/4843) | Initial release supporting the Snapchat Marketing API |

</details>
