# LinkedIn Ads

This page guides you through the process of setting up the LinkedIn Ads source connector.
The LinkedIn Ads source connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python). Airbyte uses [LinkedIn Marketing Developer Platform - API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/marketing-integrations-overview) to fetch data from LinkedIn Ads.

## Prerequisites
### For Airbyte Cloud
* The LinkedIn Ads account with permission to access data from accounts you want to sync.

### For Airbyte Open Source
* The LinkedIn Ads account with permission to access data from accounts you want to sync.
* Authentication Options:
   * OAuth2.0:
      * `Client ID` from your `Developer Application`
      * `Client Secret` from your `Developer Application`
      * `Refresh Token` obtained from successfull authorization with `Client ID` + `Client Secret`
   * Access Token:
      * `Access Token` obtained from successfull authorization with `Client ID` + `Client Secret`

## Step 1: Set up LinkedIn Ads

1. **Login to LinkedIn as the API user.**
2. **Create an App** [here](https://www.linkedin.com/developers/apps):
   * `App Name`: airbyte-source
   * `Company`: search and find your company LinkedIn page
   * `Privacy policy URL`: link to company privacy policy
   * `Business email`: developer/admin email address
   * `App logo`: Airbyte's \(or Company's\) logo
   * `Products`: Select [Marketing Developer Platform](https://www.linkedin.com/developers/apps/122632736/products/marketing-developer-platform) \(checkbox\)
   * Review/agree to legal terms and create app.
3. **Verify App**:
   * Provide the verify URL to your Company's LinkedIn Admin to verify and authorize the app.
   * Once verified, select the App in the Console [here](https://www.linkedin.com/developers/apps).
   * **Review the `Auth` tab**:
     * Record `client_id` and `client_secret` \(for later steps\).
     * Review permissions and ensure app has the permissions \(above\).
     * Oauth 2.0 settings: Provide a `redirect_uri` \(for later steps\): `https://airbyte.io`
     * Review the `Products` tab and ensure `Marketing Developer Platform` has been added and approved \(listed in the `Products` section/tab\).
     * Review the `Usage & limits` tab. This shows the daily application and user/member limits with percent used for each resource endpoint.

4. **Authorize App**:

   (Required for Airbyte Open Source, Optional for Airbyte Cloud)
   
   The authorization token `lasts  60-days before expiring`. The connector app will need to be reauthorized when the authorization token expires.

   Create an Authorization URL with the following pattern:

   * The permissions set you need to use is: `r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`
   * URL pattern: Provide the scope from permissions above \(with + delimiting each permission\) and replace the other highlighted parameters: `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`
   * Modify and open the `url` in the browser.
   * Once redirected, click `Allow` to authorize app.
   * The browser will be redirected to the `redirect_uri`. Record the `code` parameter listed in the redirect URL in the Browser header URL.

5. **Run the following curl command** using `Terminal` or `Command line` with the parameters replaced to return your  `access_token`. The `access_token` expires in 2-months.

   (Required for Airbyte Open Source, Optional for Airbyte Cloud)

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

6. **Use the `access_token`** from response from the `Step 5` to autorize LinkedIn Ads connector.

   (Required for Airbyte Open Source, Optional for Airbyte Cloud)

### Notes:

The API user account should be assigned the following permissions for the API endpoints:
Endpoints such as: `Accounts`, `Account Users`, `Ad Direct Sponsored Contents`, `Campaign Groups`, `Campaings`, `Creatives` requires the next permissions set:
* `r_ads`: read ads \(Recommended\), `rw_ads`: read-write ads
Endpoints such as: `Ad Analytics by Campaign`, `Ad Analytics by Creatives` requires the next permissions set:
* `r_ads_reporting`: read ads reporting
The complete set of permissions is:
* `r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`

The API user account should be assigned one of the following roles:
* ACCOUNT\_BILLING\_ADMIN
* ACCOUNT\_MANAGER
* CAMPAIGN\_MANAGER
* CREATIVE\_MANAGER
* VIEWER \(Recommended\)

To edit these roles, sign into Campaign Manager and follow [these instructions](https://www.linkedin.com/help/lms/answer/a496075). 

## Step 2: Set up the source connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **LinkedIn Ads** from the Source type dropdown and enter a name for this connector.
4. Add `Start Date` - the starting point for your data replication.
5. Add your `Account IDs (Optional)` if required.
6. Click `Authenticate your account`.
7. Log in and Authorize to the LinkedIn Ads account
8. click `Set up source`.

**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
3. On the Set up the source page, enter the name for the connector and select **LinkedIn Ads** from the Source type dropdown. 
4. Add `Start Date` - the starting point for your data replication.
5. Add your `Account IDs (Optional)` if required.
6. Choose between Authentication Options:
   * OAuth2.0:
      * Copy and paste info from your **LinkedIn Ads developer application**:
         * `Client ID` 
         * `Client Secret`
         * Obtain the `Refresh Token` using **Set up LinkedIn Ads** guide steps and paste it into corresponding field.
   * Access Token:
      * Obtain the `Access Token` using **Set up LinkedIn Ads** guide steps and paste it into corresponding field.
7. Click `Set up source`.

## Supported Streams and Sync Modes

This Source is capable of syncing the following data as streams:

* [Accounts](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http#search-for-accounts)
* [Account Users](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http#find-ad-account-users-by-accounts)
* [Campaign Groups](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http#search-for-campaign-groups)
* [Campaigns](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http#search-for-campaigns)
* [Creatives](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?tabs=http#search-for-creatives)
* [Ad Direct Sponsored Contents](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/create-and-manage-video?tabs=http#finders)
* [Ad Analytics by Campaign](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl#ad-analytics)
* [Ad Analytics by Creative](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl#ad-analytics) 


| Sync Mode                                 | Supported?\(Yes/No\) | 
| :---------------------------------------- | :------------------- |
| Full Refresh Overwrite Sync               | Yes                  |  
| Full Refresh Append Sync                  | Yes                  |       
| Incremental - Append Sync                 | Yes                  |       
| Incremental - Append + Deduplication Sync | Yes                  |  


### NOTE:

`Ad Direct Sponsored Contents` stream includes the information about VIDEO ADS, as well as SINGLE IMAGE ADS and other directly sponsored ads your account might have.

For Analytics Streams such as: `Ad Analytics by Campaign`, `Ad Analytics by Creative` the `pivot` column name is renamed to `_pivot` to handle the data normalization correctly and avoid name conflicts with certain destinations.

### Data type mapping

| Integration Type | Airbyte Type | Notes                      |
| :--------------- | :----------- | :------------------------- |
| `number`         | `number`     | float number               |
| `integer`        | `integer`    | whole number               |
| `date`           | `string`     | FORMAT YYYY-MM-DD          |
| `datetime`       | `string`     | FORMAT YYYY-MM-DDThh:mm:ss |
| `array`          | `array`      |                            |
| `boolean`        | `boolean`    | True/False                 |
| `string`         | `string`     |                            |


### Performance considerations

There are official Rate Limits for LinkedIn Ads API Usage, [more information here](https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits?context=linkedin/marketing/context). Rate limited requests will receive a 429 response. Rate limits specify the maximum number of API calls that can be made in a 24 hour period. These limits reset at midnight UTC every day. In rare cases, LinkedIn may also return a 429 response as part of infrastructure protection. API service will return to normal automatically. In such cases you will receive the next error message:

```text
"Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error. If the maximum of available API requests capacity is reached, you will have the following message:

```text
"Max try rate limit exceded..."
```

After 5 unsuccessful attempts - the connector will stop the sync operation. In such cases check your Rate Limits [on this page](https://www.linkedin.com/developers/apps) &gt; Choose you app &gt; Analytics. 


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                           |
|:--------| :--------- | :-----------------------------------------------------   | :---------------------------------------------------------------------------------------------------------------- |
| 0.1.9   | 2022-07-21 | [14924](https://github.com/airbytehq/airbyte/pull/14924) | Remove `additionalProperties` field from schemas                                                                   |
| 0.1.8   | 2022-06-07 | [13495](https://github.com/airbytehq/airbyte/pull/13495) | Fixed `base-normalization` issue on `Destination Redshift` caused by wrong casting of `pivot` column              |
| 0.1.7   | 2022-05-04 | [12482](https://github.com/airbytehq/airbyte/pull/12482) | Update input configuration copy                                                                                   |
| 0.1.6   | 2022-04-04 | [11690](https://github.com/airbytehq/airbyte/pull/11690) | Small documenation corrections                                                                                    |
| 0.1.5   | 2021-12-21 | [8984](https://github.com/airbytehq/airbyte/pull/8984)   | Update connector fields title/description                                                                         |
| 0.1.4   | 2021-12-02 | [8382](https://github.com/airbytehq/airbyte/pull/8382)   | Modify log message in rate-limit cases                                                                            |
| 0.1.3   | 2021-11-11 | [7839](https://github.com/airbytehq/airbyte/pull/7839)   | Added oauth support                                                                                               |
| 0.1.2   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                                                   |
| 0.1.1   | 2021-10-02 | [6610](https://github.com/airbytehq/airbyte/pull/6610)   | Fix for  `Campaigns/targetingCriteria` transformation, coerced  `Creatives/variables/values` to string by default |
| 0.1.0   | 2021-09-05 | [5285](https://github.com/airbytehq/airbyte/pull/5285)   | Initial release of Native LinkedIn Ads connector for Airbyte                                                      |

