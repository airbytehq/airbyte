# Facebook Marketing

This page contains the setup guide and reference information for Facebook Marketing.

## Prerequisites

* Facebook Developer Account
* Facebook Ad Account ID
* Facebook app with the Marketing API enabled
* Facebook Marketing API Access Token

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Create a Facebook app

1. Navigate to [Meta for Developers](https://developers.facebook.com/apps/) and follow the steps provided in the [Facebook documentation](https://developers.facebook.com/docs/development/create-an-app/) to create a Facebook app.

2. While creating the app, when you are prompted for "What do you want your app to do?", select **Other**.
![Facebook App Use Case](/docs/setup-guide/assets/images/facebook-app-usecase.jpg "Facebook App Use Case")

3. Set the app type to **Business** when prompted.
![Facebook App Type](/docs/setup-guide/assets/images/facebook-app-type.jpg "Facebook App Type")

4. Give your app a name, add a contact email, and click **Create app**.
![Facebook Create App](/docs/setup-guide/assets/images/facebook-create-app.jpg "Facebook Create App")

### Step 2: Obtain Facebook credentials

1. From your App’s Dashboard, find **Marketing API**. And Click **Set up**.
![Facebook Marketing API](/docs/setup-guide/assets/images/facebook-marketing-api.jpg "Facebook Marketing API")

2. Inside Marketing API, click **Tools**.
![Facebook Marketing API Tools](/docs/setup-guide/assets/images/facebook-marketing-api-tools.jpg "Facebook Marketing AP Tools")

3. Select all the available **Token Permissions** (ads_management, ads_read, read_insights). And then click **Get token**. Copy the generated token for later use.
![Facebook Marketing API Token](/docs/setup-guide/assets/images/facebook-marketing-api-token.jpg "Facebook Marketing API Token")

4. Request a **rate limit increase**: Facebook heavily throttles API tokens generated from Facebook apps with the default Standard Access tier, making it infeasible to use the token for syncs with Airbyte. You'll need to request an upgrade to Advanced Access for your app on the following permissions:

  > * Ads Management Standard Access
  > * ads_read
  > * Ads_management

  See the [Facebook documentation on Authorization](https://developers.facebook.com/docs/marketing-api/overview/authorization/#access-levels) to request Advanced Access to the relevant permissions.

5. Obtain your **Facebook Ad Account ID Number**: open your Meta Ads Manager. The Ad Account ID number is in the Account dropdown menu or in your browser's address bar. Refer to the [Facebook docs for more information](https://www.facebook.com/business/help/1492627900875762).

### Step 3: Set up Facebook Marketing in Daspire

1. Select **Facebook Marketing** from the Source list.

2. Enter a **Source Name**.

3. Enter the **Access Token** you obtained in Step 2.

4. Enter the **Account ID** you obtained in Step 2.

5. (Optional) For **Start Date**, enter the date programmatically in the `YYYY-MM-DDTHH:mm:ssZ` format. If not set then all data will be replicated for usual streams and only last 2 years for insight streams.

  > Note: Insight tables are only able to pull data from the last 37 months. If you are syncing insight tables and your start date is older than 37 months, your sync will fail.

6. (Optional) For **End Date**, enter the date programmatically in the `YYYY-MM-DDTHH:mm:ssZ` format. This is the date until which you'd like to replicate data for all Incremental streams. All data generated between the start date and this end date will be replicated. Not setting this option will result in always syncing the latest data.

7. (Optional) Toggle the **Include Deleted Campaigns, Ads, and AdSets** button to include data from deleted Campaigns, Ads, and AdSets.

  > The Facebook Marketing API does not have a concept of deleting records in the same way that a database does. While you can archive or delete an ad campaign, the API maintains a record of the campaign. Toggling the Include Deleted button lets you replicate records for campaigns or ads even if they were archived or deleted from the Facebook platform.

8. (Optional) Toggle the **Fetch Thumbnail Images** button to fetch the `thumbnail_url` and store the result in `thumbnail_data_url` for each [Ad Creative](https://developers.facebook.com/docs/marketing-api/creative/).

9. (Optional) In the **Custom Insights** section, you may provide a list of ad statistics entries. Each entry should have a unique name and can contain fields, breakdowns or action_breakdowns. Fields refer to the different data points you can collect from an ad, while breakdowns and action_breakdowns let you segment this data for more detailed insights. Click on Add to create a new entry in this list.

  > To retrieve specific fields from Facebook Ads Insights combined with other breakdowns, you can choose which fields and breakdowns to sync. However, please note that not all fields can be requested, and many are only functional when combined with specific other fields. For example, the breakdown app_id is only supported with the total_postbacks field. For more information on the breakdown limitations, refer to the Facebook documentation.

  To configure Custom Insights:

  i. For **Name**, enter a name for the insight. This will be used as the Daspire stream name.

  ii. (Optional) For **Level**, enter the level of granularity for the data you want to pull from the Facebook Marketing API (`account`, `ad`, `adset`, `campaign`). Set to ad by default.

  iii. (Optional) For **Fields**, use the dropdown list to select the fields you want to pull from the Facebook Marketing API.

  iv. (Optional) For **Breakdowns**, use the dropdown list to select the breakdowns you want to configure.

  v. (Optional) For **Action Breakdowns**, use the dropdown list to select the action breakdowns you want to configure.

  vi. (Optional) For **Action Report Time**, enter the action report time you want to configure. This value determines the timing used to report action statistics. For example, if a user sees an ad on Jan 1st but converts on Jan 2nd, this value will determine how the action is reported.

  > * impression: Actions are attributed to the time the ad was viewed (Jan 1st).
  > * conversion: Actions are attributed to the time the action was taken (Jan 2nd).
  > * mixed: Click-through actions are attributed to the time the ad was viewed (Jan 1st), and view-through actions are attributed to the time the action was taken (Jan 2nd).

  vii. (Optional) For **Time Increment**, you may provide a value in days by which to aggregate statistics. The sync will be chunked into intervals of this size. For example, if you set this value to 7, the sync will be chunked into 7-day intervals. The default value is 1 day.

  viii. (Optional) For **Start Date**, enter the date in the YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated. If this field is left blank, Daspire will replicate all data.

  ix. (Optional) For **End Date**, enter the date in the YYYY-MM-DDTHH:mm:ssZ format. The data added on and before this date will be replicated. If this field is left blank, Daspire will replicate the latest data.

  x. (Optional) For **Custom Insights Lookback Window**, you may set a window in days to revisit data during syncing to capture updated conversion data from the API. Facebook allows for attribution windows of up to 28 days, during which time a conversion can be attributed to an ad. If you have set a custom attribution window in your Facebook account, please set the same value here. Otherwise, you may leave it at the default value of 28. For more information on action attributions, please refer to the [Meta Help Center](https://www.facebook.com/business/help/458681590974355?id=768381033531365).

  > Note: Additional data streams for your Facebook Marketing connector are dynamically generated according to the Custom Insights you specify. If you have an existing Facebook Marketing source and you decide to update or remove some of your Custom Insights, you must also adjust the connections that sync to these streams. Specifically, you should either disable these connections or refresh the source schema associated with them to reflect the changes.

10. (Optional) For **Page Size of Requests**, you can specify the number of records per page for paginated responses. Most users do not need to set this field unless specific issues arise or there are unique use cases that require tuning the connector's settings. The default value is set to retrieve 100 records per page.

11. (Optional) For **Insights Window Lookback**, you may set a window in days to revisit data during syncing to capture updated conversion data from the API. Facebook allows for attribution windows of up to 28 days, during which time a conversion can be attributed to an ad. If you have set a custom attribution window in your Facebook account, please set the same value here. Otherwise, you may leave it at the default value of 28. For more information on action attributions, please refer to the [Meta Help Center](https://www.facebook.com/business/help/458681590974355?id=768381033531365).

12. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

* [Activities](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)
* [AdAccount](https://developers.facebook.com/docs/marketing-api/business-asset-management/guides/ad-accounts)
* [AdCreatives](https://developers.facebook.com/docs/marketing-api/reference/ad-creative#fields)
* [AdSets](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign#fields)
* [Ads](https://developers.facebook.com/docs/marketing-api/reference/adgroup#fields)
* [AdInsights](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)
* [Campaigns](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group#fields)
* [CustomConversions](https://developers.facebook.com/docs/marketing-api/reference/custom-conversion)
* [CustomAudiences](https://developers.facebook.com/docs/marketing-api/reference/custom-audience)
* [Images](https://developers.facebook.com/docs/marketing-api/reference/ad-image)
* [Videos](https://developers.facebook.com/docs/marketing-api/reference/video)

Daspire also supports the following Prebuilt Facebook Ad Insights Reports:

| Stream | Breakdowns | Action Breakdowns |
| --- | --- | --- |
| Ad Insights Action Carousel Card | --- | `action_carousel_card_id`, `action_carousel_card_name` |
| Ad Insights Action Conversion Device | `device_platform` | `action_type` |
| Ad Insights Action Product ID | `product_id` | --- |
| Ad Insights Action Reaction | --- | `action_reaction` |
| Ad Insights Action Video Sound | --- | `action_video_sound` |
| Ad Insights Action Video Type | --- | `action_video_type` |
| Ad Insights Action Type | --- | `action_type` |
| Ad Insights Age And Gender | `age`, `gender` | `action_type`, `action_target_id`, `action_destination` |
| Ad Insights Delivery Device | `device_platform` | `action_type` |
| Ad Insights Delivery Platform | `publisher_platform` | `action_type` |
| Ad Insights Delivery Platform And Device Platform | `publisher_platform`, `device_platform` | `action_type` |
| Ad Insights Demographics Age | `age` | `action_type` |
| Ad Insights Demographics Country | `country` | `action_type` |
| Ad Insights Demographics DMA Region | `dma` | `action_type` |
| Ad Insights Demographics Gender | `gender` | `action_type` |
| Ad Insights DMA | `dma` | `action_type`, `action_target_id`, `action_destination` |
| Ad Insights Country	 | `country` | `action_type`, `action_target_id`, `action_destination` |
| Ad Insights Platform And Device | `publisher_platform`, `platform_position`, `impression_device` | `action_type` |
| Ad Insights Region | `region` | `action_type`, `action_target_id`, `action_destination` |

You can segment the Ad Insights table into parts based on the following information. Each part will be synced as a separate table if normalization is enabled:

* Country
* DMA (Designated Market Area)
* Gender & Age
* Platform & Device
* Region

For more information, see the [Facebook Insights API documentation](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/).

## Facebook Marketing Attribution Reporting

The Facebook Marketing connector uses the `lookback_window` parameter to repeatedly read data from the last `<lookback_window>` days during an Incremental sync. This means some data will be synced twice (or possibly more often) despite the cursor value being up to date, in order to capture updated ads conversion data from Facebook. You can change this date window by adjusting the `lookback_window` parameter when setting up the source, up to a maximum of 28 days. Smaller values will result in fewer duplicates, while larger values provide more accurate results. For a deeper understanding of the purpose and role of the attribution window, refer to [this Meta article](https://www.facebook.com/business/help/458681590974355?id=768381033531365).

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
