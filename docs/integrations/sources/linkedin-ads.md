# LinkedIn Ads

This page guides you through the process of setting up the LinkedIn Ads source connector.

## Prerequisites

<!-- env:cloud -->
**For Airbyte Cloud:**

* The LinkedIn Ads account with permission to access data from accounts you want to sync.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

* The LinkedIn Ads account with permission to access data from accounts you want to sync.
* Authentication Options:
   * OAuth2.0:
      * `Client ID` from your `Developer Application`
      * `Client Secret` from your `Developer Application`
      * `Refresh Token` obtained from successful authorization with `Client ID` + `Client Secret`
   * Access Token:
      * `Access Token` obtained from successful authorization with `Client ID` + `Client Secret`
<!-- /env:oss -->

## Step 1: Set up LinkedIn Ads

1. [Login to LinkedIn](https://developer.linkedin.com/) with a developer account.
2. Click the **Create App** icon on the center of the page or [use here](https://www.linkedin.com/developers/apps). Fill in the required fields:  
    1. For **App Name**, enter a name.
    2. For **LinkedIn Page**, enter your company's name or LinkedIn Company Page URL.
    3. For **Privacy policy URL**, enter the link to your company's privacy policy.
    4. For **App logo**, upload your company's logo.
    5. For **Legal Agreement**, select **I have read and agree to these terms**.
    6. Click **Create App**, on the bottom right of the screen. LinkedIn redirects you to a page showing the details of your application.

3. Verify your app. You can verify your app using the following steps:
    1. To display the settings page, click the **Settings** tab. On the **App Settings** section, click **Verify** under **Company**. A popup window will be displayed. To generate the verification URL, click on **Generate URL**, then copy and send the URL to the Page Admin (this may be you). Click on **I'm done**.
    If you are the administrator of your Page, simply run the URL in a new tab (if not, an administrator will have to do the next step). Click on **Verify**. Finally, Refresh the tab of app creation, the app should now be associated with your Page.

    2.  To display the Products page, click the **Product** tab. For **Marketing Developer Platform** click on the **Request access**. A popup window will be displayed. Review and Select **I have read and agree to these terms**. Finally, click **Request access**. 
    
    3. To authorize your application, click the **Auth** tab. The authentication page is displayed. Copy the **client_id** and **client_secret** (for later steps). For **Oauth 2.0 settings**, Provide a **redirect_uri** (for later steps).
    
    4. Click and review the **Analytics** tab. This page shows the daily application and user/member limits with the percent used for each resource endpoint.


4. (Optional for Airbyte Cloud) Authorize your app. In case your authorization expires:

   The authorization token `lasts 60-days before expiring`. The connector app will need to be reauthorized when the authorization token expires.
   Create an Authorization URL with the following steps:

   1. Replace the highlighted parameters `YOUR_CLIENT_ID` and `YOUR_REDIRECT_URI` in the URL (`https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`) from the scope obtain below.

   2. Set up permissions for the following scopes `r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`. For **OAuth2.0**, copy the `Client ID`, and `Client Secret` from your `Developer Application`. And copy the `Refresh Token` obtained from successful authorization with `Client ID` + `Client Secret`

   3. Enter the modified `URL` in the browser. You will be redirected.

   4. To authorize the app, click **Allow**.

   5. Copy the `code` parameter listed in the redirect URL in the Browser header URL.
   
5. (Optional for Airbyte Cloud) Run the following curl command using `Terminal` or `Command line` with the parameters replaced to return your `access_token`. The `access_token` expires in 2-months.

   ```text
    curl -0 -v -X POST https://www.linkedin.com/oauth/v2/accessToken\
    -H "Accept: application/json"\
    -H "application/x-www-form-urlencoded"\
    -d "grant_type=authorization_code"\
    -d "code=YOUR_CODE"\
    -d "client_id=YOUR_CLIENT_ID"\
    -d "client_secret=YOUR_CLIENT_SECRET"\
    -d "redirect_uri=YOUR_REDIRECT_URI"
   ```

6. (Optional for Airbyte Cloud) Use the `access_token`. Same as the approach in  `Step 5` to authorize LinkedIn Ads connector.


### Notes:

The API user account should be assigned the following permissions for the API endpoints:
Endpoints such as: `Accounts`, `Account Users`, `Ad Direct Sponsored Contents`, `Campaign Groups`, `Campaigns`, and `Creatives` requires the following permissions set:

- `r_ads`: read ads \(Recommended\), `rw_ads`: read-write ads
  Endpoints such as: `Ad Analytics by Campaign`, and `Ad Analytics by Creatives` requires the following permissions set:
- `r_ads_reporting`: read ads reporting
  The complete set of permissions is as follows:
- `r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`

The API user account should be assigned one of the following roles:

- ACCOUNT_BILLING_ADMIN
- ACCOUNT_MANAGER
- CAMPAIGN_MANAGER
- CREATIVE_MANAGER
- VIEWER \(Recommended\)

To edit these roles, sign in to Campaign Manager and follow [these instructions](https://www.linkedin.com/help/lms/answer/a496075).

## Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Login to your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **LinkedIn Ads** from the Source type dropdown and enter a name for this connector.
4. Add `Start Date` - the starting point for your data replication.
5. Add your `Account IDs (Optional)` if required.
6. Click **Authenticate your account**.
7. Login and Authorize the LinkedIn Ads account
8. Click **Set up source**.

<!-- env:oss -->
**For Airbyte Open Source:**

1. Go to the local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the Set up the source page, enter the name for the connector and select **LinkedIn Ads** from the Source type dropdown.
4. Add `Start Date` - the starting point for your data replication.
5. Add your `Account IDs (Optional)` if required.
6. Choose between Authentication Options:
    1. For **OAuth2.0:** Copy and paste info (**Client ID**, **Client Secret**) from your **LinkedIn Ads developer application**, and obtain the **Refresh Token** using **Set up LinkedIn Ads**  guide steps and paste it into the corresponding field.
    2. For **Access Token:** Obtain the **Access Token** using **Set up LinkedIn Ads**  guide steps and paste it into the corresponding field.
7. Click **Set up source**.
<!-- /env:oss -->

## Supported Streams and Sync Modes

This Source is capable of syncing the following data as streams:

- [Accounts](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http#search-for-accounts)
- [Account Users](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http#find-ad-account-users-by-accounts)
- [Campaign Groups](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http#search-for-campaign-groups)
- [Campaigns](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http#search-for-campaigns)
- [Creatives](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?tabs=http#search-for-creatives)
- [Ad Direct Sponsored Contents](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/create-and-manage-video?tabs=http#finders)
- [Ad Analytics by Campaign](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl#ad-analytics)
- [Ad Analytics by Creative](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl#ad-analytics)

| Sync Mode                                 | Supported?\(Yes/No\) |
| :---------------------------------------- | :------------------- |
| Full Refresh Overwrite Sync               | Yes                  |
| Full Refresh Append Sync                  | Yes                  |
| Incremental - Append Sync                 | Yes                  |
| Incremental - Append + Deduplication Sync | Yes                  |

### NOTE:

The `Ad Direct Sponsored Contents` stream includes information about VIDEO ADS, as well as `SINGLE IMAGE ADS` and other directly sponsored ads your account might have.

For Analytics Streams such as `Ad Analytics by Campaign` and `Ad Analytics by Creative`, the `pivot` column name is renamed to `_pivot` to handle the data normalization correctly and avoid name conflicts with certain destinations.

### Data type mapping

| Integration Type | Airbyte Type | Notes                      |
| :--------------- | :----------- | :------------------------- |
| `number`         | `number`     | float number               |
| `integer`        | `integer`    | whole number               |
| `date`           | `string`     | FORMAT YYYY-MM-DD          |
| `datetime`       | `string`     | FORMAT YYYY-MM-DDThh:mm: ss |
| `array`          | `array`      |                            |
| `boolean`        | `boolean`    | True/False                 |
| `string`         | `string`     |                            |

### Performance considerations

LinkedIn Ads has Official Rate Limits for API Usage, [more information here](https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits?context=linkedin/marketing/context). Rate limited requests will receive a 429 response. These limits reset at midnight UTC every day. In rare cases, LinkedIn may also return a 429 response as part of infrastructure protection. API service will return to normal automatically. In such cases, you will receive the following error message:

```text
"Caught retriable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error. If the maximum available API requests capacity is reached, you will have the following message:

```text
"Max try rate limit exceeded..."
```

After 5 unsuccessful attempts - the connector will stop the sync operation. In such cases check your Rate Limits [on this page](https://www.linkedin.com/developers/apps) &gt; Choose your app &gt; Analytics.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                         |
|:--------|:-----------|:---------------------------------------------------------| :-------------------------------------------------------------------------------------------------------------- |
| 0.1.13  | 2023-01-27 | [22013](https://github.com/airbytehq/airbyte/pull/22013) | for adDirectSponsoredContents stream skip accounts which are part of organization                               |
| 0.1.12  | 2022-10-18 | [18111](https://github.com/airbytehq/airbyte/pull/18111) | for adDirectSponsoredContents stream skip accounts which are part of organization                               |
| 0.1.11  | 2022-10-07 | [17724](https://github.com/airbytehq/airbyte/pull/17724) | Retry 429/5xx errors when refreshing access token                                                               |
| 0.1.10  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream states.                                                                                   |
| 0.1.9   | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas                                                                |
| 0.1.8   | 2022-06-07 | [13495](https://github.com/airbytehq/airbyte/pull/13495) | Fixed `base-normalization` issue on `Destination Redshift` caused by wrong casting of `pivot` column            |
| 0.1.7   | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                                 |
| 0.1.6   | 2022-04-04 | [11690](https://github.com/airbytehq/airbyte/pull/11690) | Small documentation corrections                                                                                  |
| 0.1.5   | 2021-12-21 | [8984](https://github.com/airbytehq/airbyte/pull/8984)   | Update connector fields title/description                                                                       |
| 0.1.4   | 2021-12-02 | [8382](https://github.com/airbytehq/airbyte/pull/8382)   | Modify log message in rate-limit cases                                                                          |
| 0.1.3   | 2021-11-11 | [7839](https://github.com/airbytehq/airbyte/pull/7839)   | Added OAuth support                                                                                             |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                                 |
| 0.1.1   | 2021-10-02 | [6610](https://github.com/airbytehq/airbyte/pull/6610)   | Fix for `Campaigns/targetingCriteria` transformation, coerced `Creatives/variables/values` to string by default |
| 0.1.0   | 2021-09-05 | [5285](https://github.com/airbytehq/airbyte/pull/5285)   | Initial release of Native LinkedIn Ads connector for Airbyte                                                    |
