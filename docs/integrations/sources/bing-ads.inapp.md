## Prerequisites
* [Microsoft developer token](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token) of an authorized Bing Ads OAuth application

To use the Bing Ads API, you must have a developer token and valid user credentials. You will need to register an OAuth app to get a refresh token.
1. [Register your application](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-register?view=bingads-13) in the Azure portal.
2. [Request user consent](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-consent?view=bingads-13l) to get the authorization code.
3. Use the authorization code to [get a refresh token](https://docs.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13).

:::note

The refresh token expires every 90 days. Repeat the authorization process to get a new refresh token. The full authentication process described [here](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#access-token).
Please be sure to authenticate with the email (personal or work) that you used to sign in to the Bing ads/Microsoft ads platform.
:::

4. Request your [Microsoft developer token](https://docs.microsoft.com/en-us/advertising/guides/get-started?view=bingads-13#get-developer-token) in the Microsoft Advertising Developer Portal account tab. 


## Setup guide
1. Enter a name for your source.
2. Enter the developer token
3. For **Tenant ID**, enter the custom tenant or use the common tenant. If your OAuth app has a custom tenant and you cannot use Microsoft’s recommended common tenant, use the custom tenant in the Tenant ID field when you set up the connector. 

:::info
The custom tenant is used in the authentication URL, for example: `https://login.microsoftonline.com/<tenant>/oauth2/v2.0/authorize`

:::

4. For **Replication Start Date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
5. For **Lookback window** (also known as attribution or conversion window), enter the number of **days** to look into the past. If your conversion window has an hours/minutes granularity, round it up to the number of days exceeding. If you're not using performance report streams in incremental mode, let it with 0 default value.
6. Click **Authenticate your Bing Ads account** and authorize your account.
8. Click **Set up source**.  

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Bing Ads](https://docs.airbyte.com/integrations/sources/bing-ads).
