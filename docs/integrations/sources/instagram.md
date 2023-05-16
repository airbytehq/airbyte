# Instagram

This page contains the setup guide and reference information for the Instagram source connector.

## Prerequisites

* [Meta for Developers account](https://developers.facebook.com)
* [Instagram business account](https://www.facebook.com/business/help/898752960195806) to your Facebook page
* [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) to your Facebook app
* Facebook API [access token](https://developers.facebook.com/docs/facebook-login/access-tokens/#usertokens)
* [Facebook ad account ID number](https://www.facebook.com/business/help/1492627900875762) (you'll use this to configure Instagram as a source in Airbyte)

## Setup Guide

### Step 1: Set up Instagram​

Generate Access tokens with the following permissions:

* [instagram_basic](https://developers.facebook.com/docs/permissions/reference/instagram_basic)
* [instagram_manage_insights](https://developers.facebook.com/docs/permissions/reference/instagram_manage_insights)
* [pages_show_list](https://developers.facebook.com/docs/permissions/reference/pages_show_list)
* [pages_read_engagement](https://developers.facebook.com/docs/permissions/reference/pages_read_engagement)
* [Instagram Public Content Access](https://developers.facebook.com/docs/apps/features-reference/instagram-public-content-access)

To obtain Access Tokens with the necessary permissions, please follow the below steps:

1. **Create a Facebook App**: Create a Facebook Developers account and set up a Facebook App. For more details, see [Getting Started with the Graph API](https://developers.facebook.com/docs/apis-and-sdks/getting-started/).
2. **Add Instagram to your Facebook App**: Instagram can be added to your Facebook App via the Developer Dashboard following these steps:
	1. Go to your [Instagram Basic Display Settings](https://www.instagram.com/developer/clients/manage/)
	2. Click on "Register new Client ID"
	3. Fill in app details. (Contact Email is important as it will be used for Facebook review)
	4. Read and accept Platform Terms of service and Data Policy
	5. Click on Create New Client ID
	6. Once created, you will see your app, Client ID, Client Secret, and the settings on this page.
3. **Get authorized**: Next, your app must request authorization to access the APIs on behalf of Instagram business users. See [Authorizing requests with OAuth 2.0](https://developers.facebook.com/docs/instagram-basic-display-api/guides/authorization/) for details.
	1. Your app launches the Instagram login flow, which is an embedded webview that asks users to authorize the app.
	2. If the user grants the app authorization, Instagram redirects back to your specified redirect URI with an authorization code.
	3. Your app exchanges this code for an access token that can be used to interact with the [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/). 

### Step 2: Set up the Instagram connector in Airbyte

Add your Instagram account to Airbyte as the following steps:

1. Enter an arbitrary **Connection ID** in the **New connection** screen.
2. In the **Set up a Connector** screen, select **Instagram** from the list of possible connector sources.
3. Provide the details from the Access Token in **Step 1** above:	
	* **`start_date`**: The date from which you'd like to replicate data for User Insights, in the format YYYY-MM-DDT00:00:00Z. All data generated after this date will be replicated.
	* **`access_token`**: The value of the access token generated with <b>instagram_basic, instagram_manage_insights, pages_show_list, pages_read_engagement, Instagram Public Content Access</b> permissions.

To authenticate your Instagram account, click **Authenticate your Instagram account**. Through this link, Airbyte will handle the Oauth2.0 authentication flow to obtain the necessary `access_token` as described in Step 1.

After successful authentication, enter the relevant Connector specifications, then click **Set up source**.

## Supported sync modes
The Instagram source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

:::note

Incremental sync modes are only available for the [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights) stream.

:::

## Supported Streams
The Instagram source connector supports the following streams. For more information, see the [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) and [Instagram Insights API documentation](https://developers.facebook.com/docs/instagram-api/guides/insights/).

* [User](https://developers.facebook.com/docs/instagram-api/reference/ig-user)
  * [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
* [Media](https://developers.facebook.com/docs/instagram-api/reference/ig-user/media)
  * [Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)
* [Stories](https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories/)
  * [Story Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

### Rate Limiting and Performance Considerations

Instagram limits the number of requests that can be made at a time, but the Instagram connector gracefully handles rate limiting. See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/#instagram-graph-api) for more information.

## Data type map
AirbyteRecords are required to conform to the [Airbyte type](https://docs.airbyte.com/understanding-airbyte/supported-data-types/) system. This means that all sources must produce schemas and records within these types and all destinations must handle records that conform to this type system.

| Integration Type | Airbyte Type |
| :--------------- | :----------- |
| `string`         | `string`     |
| `number`         | `number`     |
| `array`          | `array`      |
| `object`         | `object`     |