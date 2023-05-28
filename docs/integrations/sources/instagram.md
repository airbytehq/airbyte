# Instagram

This page contains the setup guide and reference information for the Instagram source connector.

## Prerequisites

* [Meta for Developers account](https://developers.facebook.com)
* [Instagram business account](https://www.facebook.com/business/help/898752960195806) to your Facebook page
* [Instagram Graph API](https://developers.facebook.com/docs/instagram-api/) to your Facebook app
* [Facebook OAuth Reference](https://developers.facebook.com/docs/instagram-basic-display-api/reference)
* [Facebook ad account ID number](https://www.facebook.com/business/help/1492627900875762) (you'll use this to configure Instagram as a source in Airbyte)

## Setup Guide

### Prerequisites

Before setting up the Instagram Source connector in Airbyte, make sure you have the following:

1. An Instagram Business account or an Instagram Creator account.
2. A Facebook Page connected to the Instagram account.
3. The Facebook App with the necessary permissions.

### Step 1: Create a Facebook App

1. Go to [Facebook for Developers](https://developers.facebook.com/) and log in with your Facebook account.
2. Click **Get Started** and follow the on-screen instructions to create a Facebook Developer Account, if you don't have one already.
3. Click **Create App** and choose **For Everything Else**.
4. Provide an **App Display Name** and an **App Contact Email**, then click **Create App ID**.
5. You will be redirected to the App Dashboard. 

### Step 2: Obtain Required Permissions for Instagram API

1. On the App Dashboard, click **Products** in the left sidebar and then click **+** to add a new product.
2. Find **Instagram Basic Display** and click **Set Up** to add it to your App.
3. Scroll down to the **Add or Remove Permissions** section and add the following permissions:
   - instagram_basic
   - instagram_manage_insights
   - pages_show_list
   - pages_read_engagement
   - Instagram Public Content Access
4. Submit your app for review and receive approval from Facebook.

### Step 3: Generate Access Token

1. After your app has been reviewed and granted the necessary permissions, go to the [Access Token Debugger](https://developers.facebook.com/tools/access_token/).
2. Click **Debug** for the **User Token**.
3. In the **Debug** view, click **Extend Access Token** to generate a long-lived User Access Token, and copy it.

### Step 4: Set up the Instagram Source connector in Airbyte

1. Enter the **Start Date** in YYYY-MM-DDTHH:mm:ssZ format. All data generated after this date will be replicated. If this field is blank, Airbyte will replicate all data.
2. Paste the **Access Token** you generated in Step 3 into the **access_token** field.

After completing the configuration, click **Set up source**. Your Instagram Source connector is now ready to use in Airbyte.

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


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                         |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------|
| 1.0.6   | 2023-03-28 | [26599](https://github.com/airbytehq/airbyte/pull/26599) | Media posted before business account conversion                                                                 |
| 1.0.5   | 2023-03-28 | [24634](https://github.com/airbytehq/airbyte/pull/24634) | Add user-friendly message for no instagram_business_accounts case                                               |
| 1.0.4   | 2023-03-15 | [23671](https://github.com/airbytehq/airbyte/pull/23671) | Add info about main permissions in spec and doc links in error message to navigate user                         |
| 1.0.3   | 2023-03-14 | [24043](https://github.com/airbytehq/airbyte/pull/24043) | Do not emit incomplete records for `user_insights` stream                                                       |
| 1.0.2   | 2023-03-14 | [24042](https://github.com/airbytehq/airbyte/pull/24042) | Test publish flow                                                                                               |
| 1.0.1   | 2023-01-19 | [21602](https://github.com/airbytehq/airbyte/pull/21602) | Handle abnormally large state values                                                                            |
| 1.0.0   | 2022-09-23 | [17110](https://github.com/airbytehq/airbyte/pull/17110) | Remove custom read function and migrate to per-stream state                                                     |
| 0.1.11  | 2022-09-08 | [16428](https://github.com/airbytehq/airbyte/pull/16428) | Fix requests metrics for Reels media product type                                                               |
| 0.1.10  | 2022-09-05 | [16340](https://github.com/airbytehq/airbyte/pull/16340) | Update to latest version of the CDK (v0.1.81)                                                                   |
| 0.1.9   | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification                                       |
| 0.1.8   | 2021-08-11 | [5354](https://github.com/airbytehq/airbyte/pull/5354)   | added check for empty state and fixed tests.                                                                    |
| 0.1.7   | 2021-07-19 | [4805](https://github.com/airbytehq/airbyte/pull/4805)   | Add support for previous format of STATE.                                                                       |
| 0.1.6   | 2021-07-07 | [4210](https://github.com/airbytehq/airbyte/pull/4210)   | Refactor connector to use CDK: - improve error handling. - fix sync fail with HTTP status 400. - integrate SAT. |
