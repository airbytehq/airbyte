# Snapchat Marketing

This page guides you through the process of setting up the Snapchat Marketing source connector.

## Prerequisites

<!-- env:cloud -->
**For Airbyte Cloud:**

* A Snapchat Marketing account with permission to access data from accounts you want to sync
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

* client_id
* client_secret
* refresh_token
* start_date
<!-- /env:oss -->

## Setup guide

### Step 1: Set up Snapchat

1. [Set up Snapchat Business account](https://businesshelp.snapchat.com/s/article/get-started?language=en_US)

<!-- env:oss -->
**For Airbyte Open Source:**

2. [Activate Access to the Snapchat Marketing API](https://businesshelp.snapchat.com/s/article/api-apply?language=en_US)  
3. Add the OAuth2 app:
   * Adding the OAuth2 app requires the `redirect_url` parameter.
     - If you have the API endpoint that will handle next OAuth process - write it to this parameter.
     - If not - just use some valid url. Here's the discussion about it: [Snapchat Redirect URL - Clarity in documentation please](https://github.com/Snap-Kit/bitmoji-sample/issues/3)
   * save **Client ID** and **Client Secret**
4. Get refresh token using OAuth2 authentication workflow:
   * Open the authorize link in a browser: [https://accounts.snapchat.com/login/oauth2/authorize?response\_type=code&client\_id={client\_id}&redirect\_uri={redirect\_uri}&scope=snapchat-marketing-api&state=wmKkg0TWgppW8PTBZ20sldUmF7hwvU](https://accounts.snapchat.com/login/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=snapchat-marketing-api&state=wmKkg0TWgppW8PTBZ20sldUmF7hwvU)
   * Login & Authorize via UI
   * Locate "code" query parameter in the redirect
   * Exchange code for access token + refresh token
      ```text
      curl -X POST \  
      -d "code={one_time_use_code}" \  
      -d "client_id={client_id}" \  
      -d "client_secret={client_secret}"  \  
      -d "grant_type=authorization_code"  \  
      -d "redirect_uri=redirect_uri"  
      https://accounts.snapchat.com/login/oauth2/access_token
      ```
You will receive the API key and refresh token in response. Use this refresh token in the connector specifications.  
The useful link to Authentication process is [here](https://marketingapi.snapchat.com/docs/#authentication)
<!-- /env:oss -->

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Snapchat Marketing** from the Source type dropdown and enter a name for this connector.
4. lick `Authenticate your account`.
5. Log in and Authorize to the Snapchat account
6. Choose required Start date
7. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Snapchat Marketing** from the Source type dropdown and enter a name for this connector.
4. Add **Client ID**, **Client Secret**, **Refresh Token**
5. Choose required Start date
6. Click `Set up source`.
<!-- /env:oss -->

## Supported streams and sync modes

| Stream                  | Incremental | Key                                 |
| :---------------------- | :---------- | ----------------------------------- |
| Adaccounts              | Yes         | "id"                                |
| Ads                     | Yes         | "id"                                |
| Adsquads                | Yes         | "id"                                |
| Campaigns               | Yes         | "id"                                |
| Creatives               | Yes         | "id"                                |
| Media                   | Yes         | "id"                                |
| Organizations           | No          | "id"                                |
| Segments                | Yes         | "id"                                |
| AdaccountsStatsHourly   | Yes         | ["id", "granularity", "start_time"] |
| AdaccountsStatsDaily    | Yes         | ["id", "granularity", "start_time"] |
| AdaccountsStatsLifetime | No          | ["id", "granularity"]               |
| AdsStatsHourly          | Yes         | ["id", "granularity", "start_time"] |
| AdsStatsDaily           | Yes         | ["id", "granularity", "start_time"] |
| AdsStatsLifetime        | No          | ["id", "granularity"]               |
| AdsquadsStatsHourly     | Yes         | ["id", "granularity", "start_time"] |
| AdsquadsStatsDaily      | Yes         | ["id", "granularity", "start_time"] |
| AdsquadsStatsLifetime   | No          | ["id", "granularity"]               |
| CampaignsStatsHourly    | Yes         | ["id", "granularity", "start_time"] |
| CampaignsStatsDaily     | Yes         | ["id", "granularity", "start_time"] |
| CampaignsStatsLifetime  | No          | ["id", "granularity"]               |


## Performance considerations

Hourly streams can be slowly because they generate a lot of records.

Snapchat Marketing API has limitations to 1000 items per page.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                               |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------|
| 0.1.16  | 2023-04-20 | [20897](https://github.com/airbytehq/airbyte/pull/20897) | Add missing fields to Basic Stats schema       |    
| 0.1.15  | 2023-03-02 | [22869](https://github.com/airbytehq/airbyte/pull/22869) | Specified date formatting in specification                                                     |                                        
| 0.1.14  | 2023-02-10 | [22808](https://github.com/airbytehq/airbyte/pull/22808) | Enable default `AvailabilityStrategy`                       |
| 0.1.13  | 2023-01-27 | [22023](https://github.com/airbytehq/airbyte/pull/22023) | Set `AvailabilityStrategy` for streams explicitly to `None` |
| 0.1.12  | 2023-01-11 | [21267](https://github.com/airbytehq/airbyte/pull/21267) | Fix parse empty error response                              |
| 0.1.11  | 2022-12-23 | [20865](https://github.com/airbytehq/airbyte/pull/20865) | Handle 403 permission error                                 |
| 0.1.10  | 2022-12-15 | [20537](https://github.com/airbytehq/airbyte/pull/20537) | Run on CDK 0.15.0                                           |
| 0.1.9   | 2022-12-14 | [20498](https://github.com/airbytehq/airbyte/pull/20498) | Fix output state when no records are read                   |
| 0.1.8   | 2022-10-05 | [17596](https://github.com/airbytehq/airbyte/pull/17596) | Retry 429 and 5xx errors when refreshing access token       |
| 0.1.6   | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from specs              |
| 0.1.5   | 2022-07-13 | [14577](https://github.com/airbytehq/airbyte/pull/14577) | Added stats streams hourly, daily, lifetime                 |
| 0.1.4   | 2021-12-07 | [8429](https://github.com/airbytehq/airbyte/pull/8429)   | Update titles and descriptions                              |
| 0.1.3   | 2021-11-10 | [7811](https://github.com/airbytehq/airbyte/pull/7811)   | Add oauth2.0, fix stream_state                              |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                             |
| 0.1.1   | 2021-07-29 | [5072](https://github.com/airbytehq/airbyte/pull/5072)   | Fix bug with incorrect stream\_state value                  |
| 0.1.0   | 2021-07-26 | [4843](https://github.com/airbytehq/airbyte/pull/4843)   | Initial release supporting the Snapchat Marketing API       |