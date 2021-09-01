# LinkedIn Ads

## Sync overview

The LinkedIn Ads source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).
Airbyte uses [LinkedIn Marketing Developer Platform - API](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/marketing-integrations-overview) to fetch data from LinkedIn Ads.

### Output schema

This Source is capable of syncing the following data as streams:
* [Accounts](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-accounts?tabs=http#search-for-accounts)
* [Account Users](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-account-users?tabs=http#find-ad-account-users-by-accounts)
* [Campaign Groups](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaign-groups?tabs=http#search-for-campaign-groups)
* [Campaigns](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-campaigns?tabs=http#search-for-campaigns)
* [Creatives](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/account-structure/create-and-manage-creatives?tabs=http#search-for-creatives)
* [Ad Direct Sponsored Contents](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads/advertising-targeting/create-and-manage-video?tabs=http#finders)
* [Ad Analytics by Campaign](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl#ad-analytics)
* [Ad Analytics by Creative](https://docs.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting?tabs=curl#ad-analytics) 


### NOTE:
`Ad Direct Sponsored Contents` includes the information about VIDEO ADS, as well as SINGLE IMAGE ADS and other directly sponsored ads your account might have.

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `number` | `number` | float number |
| `integer` | `integer` | whole number |
| `date` | `string` | FORMAT YYYY-MM-DD |
| `datetime` | `string` | FORMAT YYYY-MM-DDThh:mm:ss |
| `array` | `array` |  |
| `boolean` | `boolean` | True/False |
| `string` | `string` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Overwrite Sync | Yes |  |
| Full Refresh Append Sync  | Yes |  |
| Incremental - Append Sync | Yes |  |
| Incremental - Append + Deduplication Sync | Yes |  |
| Namespaces | No |  |


### Performance considerations

There are official Rate Limits for LinkedIn Ads API Usage, [more information here](https://docs.microsoft.com/en-us/linkedin/shared/api-guide/concepts/rate-limits?context=linkedin/marketing/context).
Rate limited requests will receive a 429 response. In rare cases, LinkedIn may also return a 429 response as part of infrastructure protection. API service will return to normal automatically.
In such cases you will receive the next error message:
```
"Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```
This is expected when the connector hits the 429 - Rate Limit Exceeded HTTP Error.
If the maximum of available API requests capacity is reached, you will have the following message:
```
"Max try rate limit exceded..."
```
After 5 unsuccessful attempts - the connector will stop the sync operation. 
In such cases check your Rate Limits [on this page](https://www.linkedin.com/developers/apps) > Choose you app > Analytics


## Getting started

### Authentication
The source LinkedIn uses `access_token` provided in the UI connector's settings to make API requests. Access tokens expire after `2 months from generating date (60 days)` and require a user to manually authenticate again. If you receive a `401 invalid token response`, the error logs will state that your access token has expired and to re-authenticate your connection to generate a new token. This is described more [here](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow?context=linkedin/context).

The API user account should be assigned one of the following roles:
* ACCOUNT_BILLING_ADMIN
* ACCOUNT_MANAGER
* CAMPAIGN_MANAGER
* CREATIVE_MANAGER
* VIEWER (Recommended)

The API user account should be assigned the following permissions for the API endpoints:

Endpoints such as: 
`Accounts`, `Account Users`, `Ad Direct Sponsored Contents`, `Campaign Groups`, `Campaings`, `Creatives` requires the next permissions set:

   * `r_ads`: read ads (Recommended), `rw_ads`: read-write ads

Endpoints such as: `Ad Analytics by Campaign`, `Ad Analytics by Creatives` requires the next permissions set:

   * `r_ads_reporting`: read ads reporting

The complete set of prmissions is:
   * `r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`

### Generate the Access_Token
1. **Login to LinkedIn as the API user.**
2. **Create an App** [here](https://www.linkedin.com/developers/apps):
    * `App Name`: airbyte-source
    * `Company`: search and find your company LinkedIn page
    * `Privacy policy URL`: link to company privacy policy
    * `Business email`: developer/admin email address
    * `App logo`: Airbyte's (or Company's) logo
    * `Products`: Select [Marketing Developer Platform](https://www.linkedin.com/developers/apps/122632736/products/marketing-developer-platform) (checkbox)
    Review/agree to legal terms and create app.
3. **Verify App**:
    * Provide the verify URL to your Company's LinkedIn Admin to verify and authorize the app.
    * Once verified, select the App in the Console [here](https://www.linkedin.com/developers/apps).
    * **Review the `Auth` tab**:
      * Record `client_id` and `client_secret` (for later steps).
      * Review permissions and ensure app has the permissions (above).
      * Oauth 2.0 settings: Provide a `redirect_uri` (for later steps): `https://airbyte.io`
      * Review the `Products` tab and ensure `Marketing Developer Platform` has been added and approved (listed in the `Products` section/tab).
      * Review the `Usage & limits` tab. This shows the daily application and user/member limits with percent used for each resource endpoint.
4. **Authorize App**: (The authorization token `lasts 60-days before expiring`. The connector app will need to be reauthorized when the authorization token expires.):
    Create an Authorization URL with the following pattern:
    * The permissions set you need to use is: `r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`
    * URL pattern: Provide the scope from permissions above (with + delimiting each permission) and replace the other highlighted parameters: `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=r_emailaddress,r_liteprofile,r_ads,r_ads_reporting,r_organization_social`
    * Modify and open the `url` in the browser.
    * Once redirected, click `Allow` to authorize app.
    * The browser will be redirected to the `redirect_uri`. Record the `code` parameter listed in the redirect URL in the Browser header URL.
5. **Run the following curl command** using `Terminal` or `Command line` with the parameters replaced to return your `access_token`. The `access_token` expires in 2-months.
    ```
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

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :--------    | :------ |
| 0.1.0   | 2021-09-05 | [5285](https://github.com/airbytehq/airbyte/pull/5285) | Initial release of Native LinkedIn Ads connector for Airbyte |
