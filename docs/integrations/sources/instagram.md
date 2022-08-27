# Instagram

This page guides you through the process of setting up the instagram source connector.


## Prerequisites

* A Facebook App
* An Instagram Business Account
* A Facebook Page linked to your Instagram Business Account
* A Facebook API Access Token


## Step 1: Set up Instagram

### Facebook App

#### If you don't have a Facebook App

Visit the [Facebook Developers App hub](https://developers.facebook.com/apps/) and create an App and choose "Manage Business Integrations" as the purpose of the app. Fill out the remaining fields to create your app.

### Facebook Page

See the Facebook [support](https://www.facebook.com/business/help/898752960195806) for information about how to add an Instagram Account to your Facebook Page.

### Instagram Business Account

Follow the [Instagram documentation](https://www.facebook.com/business/help/1492627900875762) for setting up an Instagram business account. We'll need this ID to configure Instagram as a source in Airbyte.


## Step 2: Set up the Instagram connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account. 
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
3. On the source setup page, select **Instagram** from the Source type dropdown and enter a name for this connector. 
4. Select `Authenticate your account`.
5. Log in and Authorize to the Instagram account and click `Set up source`.

**For Airbyte Open Source:**

1. For using an Access Tokens, set up instagram (see step above). 
2. Generate [Access Tokens](https://developers.facebook.com/docs/facebook-login/access-tokens/#usertokens) with the following permissions:
* [instagram\_basic](https://developers.facebook.com/docs/permissions/reference/instagram_basic)
* [instagram\_manage\_insights](https://developers.facebook.com/docs/permissions/reference/instagram_manage_insights)
* [pages\_show\_list](https://developers.facebook.com/docs/permissions/reference/pages_show_list)
* [pages\_read\_engagement](https://developers.facebook.com/docs/permissions/reference/pages_read_engagement)
* [Instagram Public Content Access](https://developers.facebook.com/docs/apps/features-reference/instagram-public-content-access)
3. Go to local Airbyte page.
4. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
5. On the Set up the source page, enter the name for the Instagram connector and select **Instagram** from the Source type dropdown. 
6. Paste your Access Tokens from step 2. 
7. Click `Set up source`.


## Supported sync modes

The Instagram source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental


## Supported Streams

* [User](https://developers.facebook.com/docs/instagram-api/reference/ig-user)
  * [User Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights)
* [Media](https://developers.facebook.com/docs/instagram-api/reference/ig-user/media)
  * [Media Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)
* [Stories](https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories/)
  * [Story Insights](https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights)

For more information, see the [Instagram API](https://developers.facebook.com/docs/instagram-api/) and [Instagram Insights API documentation](https://developers.facebook.com/docs/instagram-api/guides/insights/).


### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes | only User Insights |

### Rate Limiting & Performance Considerations

Instagram, like all Facebook services, has a limit on the number of requests, but Instagram connector gracefully handles rate limiting.

See Facebook's [documentation on rate limiting](https://developers.facebook.com/docs/graph-api/overview/rate-limiting/#instagram-graph-api) for more information.


## Data type map

| Integration Type | Airbyte Type |
| :--- | :--- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |


## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.9 | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438) | Annotate Oauth2 flow initialization parameters in connector specification |
| 0.1.8 | 2021-08-11 | [5354](https://github.com/airbytehq/airbyte/pull/5354) | added check for empty state and fixed tests. |
| 0.1.7 | 2021-07-19 | [4805](https://github.com/airbytehq/airbyte/pull/4805) | Add support for previous format of STATE. |
| 0.1.6 | 2021-07-07 | [4210](https://github.com/airbytehq/airbyte/pull/4210) | Refactor connector to use CDK: - improve error handling. - fix sync fail with HTTP status 400. - integrate SAT. |
