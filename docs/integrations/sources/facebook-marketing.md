# Facebook Marketing

<HideInUI>

This page contains the setup guide and reference information for the [Facebook Marketing](https://developers.facebook.com) source connector.

</HideInUI>

## Prerequisites

- A [Facebook Ad Account ID](https://www.facebook.com/business/help/1492627900875762)
<!-- env:cloud -->
-  **For Airbyte Cloud**: If you are not the owner/admin of the Ad account, you must be granted [permissions to access the Ad account](https://www.facebook.com/business/help/155909647811305?id=829106167281625) by an admin.
<!-- /env:cloud -->
<!-- env:oss -->
-  **For Airbyte Open Source**: 
   - [Facebook app](https://developers.facebook.com/apps/) with the Marketing API enabled 
   - The following permissions: [ads_management](https://developers.facebook.com/docs/permissions#a), [ads_read](https://developers.facebook.com/docs/permissions#a), [business_management](https://developers.facebook.com/docs/permissions#b) and [read_insights](https://developers.facebook.com/docs/permissions#r). 
<!-- /env:oss -->

## Setup guide

### Set up Facebook Marketing

<!-- env:cloud -->
#### For Airbyte Cloud: 

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Facebook Marketing from the Source type dropdown.
4. Enter a name for the Facebook Marketing connector.
5. To authenticate the connection, click **Authenticate your account** to authorize your Facebook account. Ensure you are logged into the right account, as Airbyte will authenticate the account you are currently logged in to.
<!-- /env:cloud -->

<!-- env:oss -->
#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Facebook Marketing from the Source type dropdown.
4. Enter a name for the Facebook Marketing connector.
<FieldAnchor field="access_token">
5. In the **Access Token** field, enter the Marketing API access token.
   
#### (For Airbyte Open Source) Generate an access token and request a rate limit increase

To set up Facebook Marketing as a source in Airbyte Open Source, you will first need to create a Facebook app and generate a Marketing API access token. You will then need to request a rate limit increase from Facebook to ensure your syncs are successful. 

1. Navigate to [Meta for Developers](https://developers.facebook.com/apps/) and follow the steps provided in the [Facebook documentation](https://developers.facebook.com/docs/development/create-an-app/) to create a Facebook app.
2. While creating the app, when you are prompted for "What do you want your app to do?", select **Other**. You will also need to set the app type to **Business** when prompted.
3. From your App’s dashboard, [set up the Marketing API](https://developers.facebook.com/docs/marketing-apis/get-started).
4. Generate a Marketing API access token: From your App’s Dashboard, click **Marketing API** --> **Tools**. Select all the available token permissions (`ads_management`, `ads_read`, `read_insights`, `business_management`) and click **Get token**. Copy the generated token for later use.
5. Request a rate limit increase: Facebook [heavily throttles](https://developers.facebook.com/docs/marketing-api/overview/authorization#limits) API tokens generated from Facebook apps with the default Standard Access tier, making it infeasible to use the token for syncs with Airbyte. You'll need to request an upgrade to Advanced Access for your app on the following permissions:

   - Ads Management Standard Access
   - ads_read
   - Ads_management

   See the Facebook [documentation on Authorization](https://developers.facebook.com/docs/marketing-api/overview/authorization/#access-levels) to request Advanced Access to the relevant permissions.

:::tip
You can use the [Access Token Tool](https://developers.facebook.com/tools/accesstoken) at any time to view your existing access tokens, including their assigned permissions and lifecycles.
:::
</FieldAnchor>
<!-- /env:oss -->

#### Facebook Marketing Source Settings
<FieldAnchor field="account_ids">
1. For **Account ID(s)**, enter one or multiple comma-separated [Facebook Ad Account ID Numbers](https://www.facebook.com/business/help/1492627900875762) to use when pulling data from the Facebook Marketing API. To find this ID, open your Meta Ads Manager. The Ad Account ID number is in the **Account** dropdown menu or in your browser's address bar. Refer to the [Facebook docs](https://www.facebook.com/business/help/1492627900875762) for more information.
</FieldAnchor>

<FieldAnchor field="start_date">
2. (Optional) For **Start Date**, use the provided datepicker, or enter the date programmatically in the `YYYY-MM-DDTHH:mm:ssZ` format. If the start date is not set, then all data will be replicated except for `Insight` data, which only pulls data for the last 37 months.

   :::info
   Insight tables are only able to pull data from the last 37 months. If you are syncing insight tables and your start date is older than 37 months, your sync will not succeed for those streams.
   :::

</FieldAnchor>

<FieldAnchor field="end_date">
3. (Optional) For **End Date**, use the provided datepicker, or enter the date programmatically in the `YYYY-MM-DDTHH:mm:ssZ` format. This is the date until which you'd like to replicate data for all Incremental streams. All data generated between the start date and this end date will be replicated. Not setting this option will result in always syncing the latest data.
</FieldAnchor>

<FieldAnchor field="campaign_statuses">
4. (Optional) Multiselect the **Campaign Statuses** to include data from Campaigns for particular statuses.
</FieldAnchor>

<FieldAnchor field="adset_statuses">
5. (Optional) Multiselect the **AdSet Statuses** to include data from AdSets for particular statuses.
</FieldAnchor>

<FieldAnchor field="ad_statuses">
6. (Optional) Multiselect the **Ad Statuses** to include data from Ads for particular statuses.
</FieldAnchor>

<FieldAnchor field="fetch_thumbnail_images">
7. (Optional) Toggle the **Fetch Thumbnail Images** button to fetch the `thumbnail_url` and store the result in `thumbnail_data_url` for each [Ad Creative](https://developers.facebook.com/docs/marketing-api/creative/).
</FieldAnchor>

<FieldAnchor field="custom_insights">
8. (Optional) In the **Custom Insights** section, you may provide a list of ad statistics entries. Each entry should have a unique name and can contain fields, breakdowns or action_breakdowns. Fields refer to the different data points you can collect from an ad, while breakdowns and action_breakdowns let you segment this data for more detailed insights. Click on **Add** to create a new entry in this list.

To retrieve specific fields from Facebook Ads Insights combined with other breakdowns, you can choose which fields and breakdowns to sync. However, please note that not all fields can be requested, and many are only functional when combined with specific other fields. For example, the breakdown `app_id` is only supported with the `total_postbacks` field. For more information on the breakdown limitations, refer to the [Facebook documentation](https://developers.facebook.com/docs/marketing-api/insights/breakdowns).

   :::info
   Additional data streams for your Facebook Marketing connector are dynamically generated according to the Custom Insights you specify. If you have an existing Facebook Marketing source and you decide to update or remove some of your Custom Insights, you must also update the connections to sync these streams by refreshing the schema.
   :::
</FieldAnchor>

   To configure Custom Insights:
<FieldAnchor field="custom_insights.name">
   1. For **Name**, enter a name for the insight. This will be used as the Airbyte stream name.
</FieldAnchor>

<FieldAnchor field="custom_insights.level">
   2. (Optional) For **Level**, enter the level of granularity for the data you want to pull from the Facebook Marketing API (`account`, `ad`, `adset`, `campaign`). Set to `ad` by default.
</FieldAnchor>

<FieldAnchor field="custom_insights.fields">
   3. (Optional) For **Fields**, use the dropdown list to select the fields you want to pull from the Facebook Marketing API.
</FieldAnchor>

<FieldAnchor field="custom_insights.breakdowns">
   4. (Optional) For **Breakdowns**, use the dropdown list to select the breakdowns you want to configure.
</FieldAnchor>

<FieldAnchor field="custom_insights.action_breakdowns">
   5. (Optional) For **Action Breakdowns**, use the dropdown list to select the action breakdowns you want to configure.
</FieldAnchor>

<FieldAnchor field="custom_insights.action_report_time">
   6. (Optional) For **Action Report Time**, enter the action report time you want to configure. This value determines the timing used to report action statistics. For example, if a user sees an ad on Jan 1st but converts on Jan 2nd, this value will determine how the action is reported.

      - `impression`: Actions are attributed to the time the ad was viewed (Jan 1st).
      - `conversion`: Actions are attributed to the time the action was taken (Jan 2nd).
      - `mixed`: Click-through actions are attributed to the time the ad was viewed (Jan 1st), and view-through actions are attributed to the time the action was taken (Jan 2nd).
</FieldAnchor>

<FieldAnchor field="custom_insights.time_increment">
   7. (Optional) For **Time Increment**, you may provide a value in days by which to aggregate statistics. The sync will be chunked into intervals of this size. For example, if you set this value to 7, the sync will be chunked into 7-day intervals. The default value is 1 day.
</FieldAnchor>

<FieldAnchor field="custom_insights.start_date">
   8. (Optional) For **Start Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is left blank, Airbyte will replicate all data.
</FieldAnchor>

<FieldAnchor field="custom_insights.end_date">
   9. (Optional) For **End Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and before this date will be replicated. If this field is left blank, Airbyte will replicate the latest data.
</FieldAnchor>

<FieldAnchor field="custom_insights.insights_lookback_window">
   10. (Optional) For **Custom Insights Lookback Window**, you may set a window in days to revisit data during syncing to capture updated conversion data from the API. Facebook allows for attribution windows of up to 28 days, during which time a conversion can be attributed to an ad. If you have set a custom attribution window in your Facebook account, please set the same value here. Otherwise, you may leave it at the default value of 28. For more information on action attributions, please refer to [the Meta Help Center](https://www.facebook.com/business/help/458681590974355?id=768381033531365).
</FieldAnchor>

<FieldAnchor field="page_size">
9. (Optional) For **Page Size of Requests**, you can specify the number of records per page for paginated responses. Most users do not need to set this field unless specific issues arise or there are unique use cases that require tuning the connector's settings. The default value is set to retrieve 100 records per page.
</FieldAnchor>

<FieldAnchor field="insights_lookback_window">
10. (Optional) For **Insights Window Lookback**, you may set a window in days to revisit data during syncing to capture updated conversion data from the API. Facebook allows for attribution windows of up to 28 days, during which time a conversion can be attributed to an ad. If you have set a custom attribution window in your Facebook account, please set the same value here. Otherwise, you may leave it at the default value of 28. For more information on action attributions, please refer to [the Meta Help Center](https://www.facebook.com/business/help/458681590974355?id=768381033531365).
</FieldAnchor>

<FieldAnchor field="insights_job_timeout">
11. (Optional) For **Insights Job Timeout**, you may set a custom value in range from 10 to 60. It establishes the maximum amount of time (in minutes) of waiting for the report job to complete.
</FieldAnchor>

12. Click **Set up source** and wait for the tests to complete.

<HideInUI>

## Supported sync modes

The Facebook Marketing source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-overwrite/)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) (except for the AdCreatives and AdAccount tables)
- [Incremental Sync - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped) (except for the AdCreatives and AdAccount tables)

## Supported Streams

- [Activities](https://developers.facebook.com/docs/marketing-api/reference/ad-activity)
- [AdAccount](https://developers.facebook.com/docs/marketing-api/business-asset-management/guides/ad-accounts)
- [AdCreatives](https://developers.facebook.com/docs/marketing-api/reference/ad-creative#fields)
- [AdSets](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign#fields)
- [Ads](https://developers.facebook.com/docs/marketing-api/reference/adgroup#fields)
- [AdInsights](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)
- [Campaigns](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group#fields)
- [CustomConversions](https://developers.facebook.com/docs/marketing-api/reference/custom-conversion)
- [CustomAudiences](https://developers.facebook.com/docs/marketing-api/reference/custom-audience)
  :::info Custom Audiences
  The `rule` field in the `Custom Audiences` stream may not be synced for all records due to limitations with the Facebook Marketing API. Syncing this field may also cause your sync to return the error message `Please reduce the amount of data` See our Troubleshooting section for more information.
  :::
- [Images](https://developers.facebook.com/docs/marketing-api/reference/ad-image)
- [Videos](https://developers.facebook.com/docs/marketing-api/reference/video)

Airbyte also supports the following Prebuilt Facebook Ad Insights Reports:

| Stream                                            |                           Breakdowns                           |                    Action Breakdowns                    |
| :------------------------------------------------ | :------------------------------------------------------------: | :-----------------------------------------------------: |
| Ad Insights Action Carousel Card                  |                              ---                               | `action_carousel_card_id`, `action_carousel_card_name`  |
| Ad Insights Action Conversion Device              |                       `device_platform`                        |                      `action_type`                      |
| Ad Insights Action Product ID                     |                          `product_id`                          |                           ---                           |
| Ad Insights Action Reaction                       |                              ---                               |                    `action_reaction`                    |
| Ad Insights Action Video Sound                    |                              ---                               |                  `action_video_sound`                   |
| Ad Insights Action Video Type                     |                              ---                               |                   `action_video_type`                   |
| Ad Insights Action Type                           |                              ---                               |                      `action_type`                      |
| Ad Insights Age And Gender                        |                        `age`, `gender`                         | `action_type`, `action_target_id`, `action_destination` |
| Ad Insights Delivery Device                       |                       `device_platform`                        |                      `action_type`                      |
| Ad Insights Delivery Platform                     |                      `publisher_platform`                      |                      `action_type`                      |
| Ad Insights Delivery Platform And Device Platform |            `publisher_platform`, `device_platform`             |                      `action_type`                      |
| Ad Insights Demographics Age                      |                             `age`                              |                      `action_type`                      |
| Ad Insights Demographics Country                  |                           `country`                            |                      `action_type`                      |
| Ad Insights Demographics DMA Region               |                             `dma`                              |                      `action_type`                      |
| Ad Insights Demographics Gender                   |                            `gender`                            |                      `action_type`                      |
| Ad Insights DMA                                   |                             `dma`                              | `action_type`, `action_target_id`, `action_destination` |
| Ad Insights Country                               |                           `country`                            | `action_type`, `action_target_id`, `action_destination` |
| Ad Insights Platform And Device                   | `publisher_platform`, `platform_position`, `impression_device` |                      `action_type`                      |
| Ad Insights Region                                |                            `region`                            | `action_type`, `action_target_id`, `action_destination` |

You can segment the Ad Insights table into parts based on the following information. Each part will be synced as a separate table if normalization is enabled:

- Country
- DMA (Designated Market Area)
- Gender & Age
- Platform & Device
- Region

For more information, see the [Facebook Insights API documentation.](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)

<!-- Christo: the note below was commented out as its accuracy could not be verified. If it can be verified and clarified for users, it should be added back in.

:::note
Please be aware that some fields, such as `conversions` and `conversion_values`, may not be directly accessible when querying Ad Insights. For comprehensive access to all available fields, we recommend using a Custom Insight and specifying the necessary **breakdowns**.
::: -->

### Entity-Relationship Diagram (ERD)
<EntityRelationshipDiagram></EntityRelationshipDiagram>

## Facebook Marketing Attribution Reporting

The Facebook Marketing connector uses the `lookback_window` parameter to repeatedly read data from the last `<lookback_window>` days during an Incremental sync. This means some data will be synced twice (or possibly more often) despite the cursor value being up to date, in order to capture updated ads conversion data from Facebook. You can change this date window by adjusting the `lookback_window` parameter when setting up the source, up to a maximum of 28 days. Smaller values will result in fewer duplicates, while larger values provide more accurate results. For a deeper understanding of the purpose and role of the attribution window, refer to this [Meta article](https://www.facebook.com/business/help/458681590974355?id=768381033531365).

## Data type map

| Integration Type | Airbyte Type |
|:----------------:|:------------:|
|      string      |    string    |
|      number      |    number    |
|      array       |    array     |
|      object      |    object    |

## Troubleshooting

### Handling "_Please reduce the amount of data you're asking for, then retry your request_" response from Facebook Graph API

This response indicates that the Facebook Graph API requires you to reduce the fields (amount of data) requested. To resolve this issue:

1. **Go to the Schema Tab**: Navigate to the schema tab of your connection.
2. **Select the Source**: Click on the source that is having issues with synchronization.
3. **Toggle Fields**: Unselect (toggle off) the fields you do not require. This action will ensure that these fields are not requested from the Graph API.
</HideInUI>

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                                                                           |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3.3.25 | 2025-01-11 | [51080](https://github.com/airbytehq/airbyte/pull/51080) | Update dependencies |
| 3.3.24 | 2025-01-04 | [50922](https://github.com/airbytehq/airbyte/pull/50922) | Update dependencies |
| 3.3.23 | 2024-12-28 | [50533](https://github.com/airbytehq/airbyte/pull/50533) | Update dependencies |
| 3.3.22 | 2024-12-21 | [50014](https://github.com/airbytehq/airbyte/pull/50014) | Update dependencies |
| 3.3.21 | 2024-12-14 | [49197](https://github.com/airbytehq/airbyte/pull/49197) | Update dependencies |
| 3.3.20 | 2024-11-25 | [48632](https://github.com/airbytehq/airbyte/pull/48632) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 3.3.19 | 2024-11-04 | [48155](https://github.com/airbytehq/airbyte/pull/48155) | Update dependencies |
| 3.3.18 | 2024-10-29 | [47894](https://github.com/airbytehq/airbyte/pull/47894) | Update dependencies |
| 3.3.17 | 2024-10-28 | [43787](https://github.com/airbytehq/airbyte/pull/43787) | Update dependencies |
| 3.3.16 | 2024-07-15 | [46546](https://github.com/airbytehq/airbyte/pull/46546) | Raise exception on missing stream |
| 3.3.15 | 2024-07-15 | [42562](https://github.com/airbytehq/airbyte/pull/42562) | Add friendly messages for "reduce fields" and "start date" errors |
| 3.3.14 | 2024-07-15 | [41958](https://github.com/airbytehq/airbyte/pull/41958) | Update cdk to filter invalid fields from configured catalog |
| 3.3.13 | 2024-07-13 | [41732](https://github.com/airbytehq/airbyte/pull/41732) | Update dependencies |
| 3.3.12 | 2024-07-11 | [41644](https://github.com/airbytehq/airbyte/pull/41644) | Remove discriminator with missing schemas |
| 3.3.11 | 2024-07-10 | [41039](https://github.com/airbytehq/airbyte/pull/41039) | Pick request fields from configured json schema properties if present |
| 3.3.10 | 2024-07-10 | [41458](https://github.com/airbytehq/airbyte/pull/41458) | Update dependencies |
| 3.3.9 | 2024-07-09 | [41106](https://github.com/airbytehq/airbyte/pull/41106) | Update dependencies |
| 3.3.8 | 2024-07-06 | [40934](https://github.com/airbytehq/airbyte/pull/40934) | Update dependencies |
| 3.3.7 | 2024-07-01 | [40645](https://github.com/airbytehq/airbyte/pull/40645) | Use latest `CDK` version possible |
| 3.3.6 | 2024-06-24 | [40241](https://github.com/airbytehq/airbyte/pull/40241) | Update AdsInsights fields - removed `adset_start` |
| 3.3.5 | 2024-06-26 | [40545](https://github.com/airbytehq/airbyte/pull/40545) | Fixed issue when the `STATE` is literal `None` (RFR) |
| 3.3.4 | 2024-06-25 | [40485](https://github.com/airbytehq/airbyte/pull/40485) | Update dependencies |
| 3.3.3 | 2024-06-22 | [40191](https://github.com/airbytehq/airbyte/pull/40191) | Update dependencies |
| 3.3.2 | 2024-06-06 | [39174](https://github.com/airbytehq/airbyte/pull/39174) | [autopull] Upgrade base image to v1.2.2 |
| 3.3.1 | 2024-06-15 | [39511](https://github.com/airbytehq/airbyte/pull/39511) | Fix validation of the spec `custom_insights.time_increment` field |
| 3.3.0 | 2024-06-30 | [33648](https://github.com/airbytehq/airbyte/pull/33648) | Add support to field `source_instagram_media_id` to `ad_creatives` report |
| 3.2.0 | 2024-06-05 | [37625](https://github.com/airbytehq/airbyte/pull/37625) | Source Facebook-Marketing: Add Selectable Auth |
| 3.1.0 | 2024-06-01 | [38845](https://github.com/airbytehq/airbyte/pull/38845) | Update AdsInsights fields - removed   `cost_per_conversion_lead` and `conversion_lead_rate` |
| 3.0.0 | 2024-04-30 | [36608](https://github.com/airbytehq/airbyte/pull/36608) | Update `body_asset, call_to_action_asset, description_asset, image_asset, link_url_asset, title_asset, video_asset` breakdowns schema. |
| 2.1.9 | 2024-05-17 | [38301](https://github.com/airbytehq/airbyte/pull/38301) | Fix data inaccuracies when `wish_bid` is requested |
| 2.1.8 | 2024-05-07 | [37771](https://github.com/airbytehq/airbyte/pull/37771) | Handle errors without API error codes/messages |
| 2.1.7 | 2024-04-24 | [36634](https://github.com/airbytehq/airbyte/pull/36634) | Update to CDK 0.80.0 |
| 2.1.6 | 2024-04-24 | [36634](https://github.com/airbytehq/airbyte/pull/36634) | Schema descriptions |
| 2.1.5 | 2024-04-17 | [37341](https://github.com/airbytehq/airbyte/pull/37341) | Move rate limit errors to transient errors. |
| 2.1.4 | 2024-04-16 | [37367](https://github.com/airbytehq/airbyte/pull/37367) | Skip config migration when the legacy account_id field does not exist |
| 2.1.3 | 2024-04-16 | [37320](https://github.com/airbytehq/airbyte/pull/37320) | Add retry for transient error |
| 2.1.2 | 2024-03-29 | [36689](https://github.com/airbytehq/airbyte/pull/36689) | Fix key error `account_id` for custom reports. |
| 2.1.1 | 2024-03-18 | [36025](https://github.com/airbytehq/airbyte/pull/36025) | Fix start_date selection behaviour |
| 2.1.0 | 2024-03-12 | [35978](https://github.com/airbytehq/airbyte/pull/35978) | Upgrade CDK to start emitting record counts with state and full refresh state |
| 2.0.1 | 2024-03-08 | [35913](https://github.com/airbytehq/airbyte/pull/35913) | Fix lookback window |
| 2.0.0 | 2024-03-01 | [35746](https://github.com/airbytehq/airbyte/pull/35746) | Update API to `v19.0` |
| 1.4.2 | 2024-02-22 | [35539](https://github.com/airbytehq/airbyte/pull/35539) | Add missing config migration from `include_deleted` field |
| 1.4.1 | 2024-02-21 | [35467](https://github.com/airbytehq/airbyte/pull/35467) | Fix error with incorrect state transforming in the 1.4.0 version |
| 1.4.0 | 2024-02-20 | [32449](https://github.com/airbytehq/airbyte/pull/32449) | Replace "Include Deleted Campaigns, Ads, and AdSets" option in configuration with specific statuses selection per stream |
| 1.3.3 | 2024-02-15 | [35061](https://github.com/airbytehq/airbyte/pull/35061) | Add integration tests |
| 1.3.2 | 2024-02-12 | [35178](https://github.com/airbytehq/airbyte/pull/35178) | Manage dependencies with Poetry |
| 1.3.1 | 2024-02-05 | [34845](https://github.com/airbytehq/airbyte/pull/34845) | Add missing fields to schemas |
| 1.3.0 | 2024-01-09 | [33538](https://github.com/airbytehq/airbyte/pull/33538) | Updated the `Ad Account ID(s)` property to support multiple IDs |
| 1.2.3   | 2024-01-04 | [33934](https://github.com/airbytehq/airbyte/pull/33828) | Make ready for airbyte-lib                                                                                                                                                                                                                                                                        |
| 1.2.2   | 2024-01-02 | [33828](https://github.com/airbytehq/airbyte/pull/33828) | Add insights job timeout to be an option, so a user can specify their own value                                                                                                                                                                                                                   |
| 1.2.1   | 2023-11-22 | [32731](https://github.com/airbytehq/airbyte/pull/32731) | Removed validation that blocked personal ad accounts during `check`                                                                                                                                                                                                                               |
| 1.2.0   | 2023-10-31 | [31999](https://github.com/airbytehq/airbyte/pull/31999) | Extend the `AdCreatives` stream schema                                                                                                                                                                                                                                                            |
| 1.1.17  | 2023-10-19 | [31599](https://github.com/airbytehq/airbyte/pull/31599) | Base image migration: remove Dockerfile and use the python-connector-base image                                                                                                                                                                                                                   |
| 1.1.16  | 2023-10-11 | [31284](https://github.com/airbytehq/airbyte/pull/31284) | Fix error occurring when trying to access the `funding_source_details` field of the `AdAccount` stream                                                                                                                                                                                            |
| 1.1.15  | 2023-10-06 | [31132](https://github.com/airbytehq/airbyte/pull/31132) | Fix permission error for `AdAccount` stream                                                                                                                                                                                                                                                       |
| 1.1.14  | 2023-09-26 | [30758](https://github.com/airbytehq/airbyte/pull/30758) | Exception should not be raises if a stream is not found                                                                                                                                                                                                                                           |
| 1.1.13  | 2023-09-22 | [30706](https://github.com/airbytehq/airbyte/pull/30706) | Performance testing - include socat binary in docker image                                                                                                                                                                                                                                        |
| 1.1.12  | 2023-09-22 | [30655](https://github.com/airbytehq/airbyte/pull/30655) | Updated doc; improved schema for custom insight streams; updated SAT or custom insight streams; removed obsolete optional max_batch_size option from spec                                                                                                                                         |
| 1.1.11  | 2023-09-21 | [30650](https://github.com/airbytehq/airbyte/pull/30650) | Fix None issue since start_date is optional                                                                                                                                                                                                                                                       |
| 1.1.10  | 2023-09-15 | [30485](https://github.com/airbytehq/airbyte/pull/30485) | added 'status' and 'configured_status' fields for campaigns stream schema                                                                                                                                                                                                                         |
| 1.1.9   | 2023-08-31 | [29994](https://github.com/airbytehq/airbyte/pull/29994) | Removed batch processing, updated description in specs, added user-friendly error message, removed start_date from required attributes                                                                                                                                                            |
| 1.1.8   | 2023-09-04 | [29666](https://github.com/airbytehq/airbyte/pull/29666) | Adding custom field `boosted_object_id` to a streams schema in `campaigns` catalog `CustomAudiences`                                                                                                                                                                                              |
| 1.1.7   | 2023-08-21 | [29674](https://github.com/airbytehq/airbyte/pull/29674) | Exclude `rule` from stream `CustomAudiences`                                                                                                                                                                                                                                                      |
| 1.1.6   | 2023-08-18 | [29642](https://github.com/airbytehq/airbyte/pull/29642) | Stop batch requests if only 1 left in a batch                                                                                                                                                                                                                                                     |
| 1.1.5   | 2023-08-18 | [29610](https://github.com/airbytehq/airbyte/pull/29610) | Automatically reduce batch size                                                                                                                                                                                                                                                                   |
| 1.1.4   | 2023-08-08 | [29412](https://github.com/airbytehq/airbyte/pull/29412) | Add new custom_audience stream                                                                                                                                                                                                                                                                    |
| 1.1.3   | 2023-08-08 | [29208](https://github.com/airbytehq/airbyte/pull/29208) | Add account type validation during check                                                                                                                                                                                                                                                          |
| 1.1.2   | 2023-08-03 | [29042](https://github.com/airbytehq/airbyte/pull/29042) | Fix broken `advancedAuth` references for `spec`                                                                                                                                                                                                                                                   |
| 1.1.1   | 2023-07-26 | [27996](https://github.com/airbytehq/airbyte/pull/27996) | Remove reference to authSpecification                                                                                                                                                                                                                                                             |
| 1.1.0   | 2023-07-11 | [26345](https://github.com/airbytehq/airbyte/pull/26345) | Add new `action_report_time` attribute to `AdInsights` class                                                                                                                                                                                                                                      |
| 1.0.1   | 2023-07-07 | [27979](https://github.com/airbytehq/airbyte/pull/27979) | Added the ability to restore the reduced request record limit after the successful retry, and handle the `unknown error` (code 99) with the retry strategy                                                                                                                                        |
| 1.0.0   | 2023-07-05 | [27563](https://github.com/airbytehq/airbyte/pull/27563) | Migrate to FB SDK version 17                                                                                                                                                                                                                                                                      |
| 0.5.0   | 2023-06-26 | [27728](https://github.com/airbytehq/airbyte/pull/27728) | License Update: Elv2                                                                                                                                                                                                                                                                              |
| 0.4.3   | 2023-05-12 | [27483](https://github.com/airbytehq/airbyte/pull/27483) | Reduce replication start date by one more day                                                                                                                                                                                                                                                     |
| 0.4.2   | 2023-06-09 | [27201](https://github.com/airbytehq/airbyte/pull/27201) | Add `complete_oauth_server_output_specification` to spec                                                                                                                                                                                                                                          |
| 0.4.1   | 2023-06-02 | [26941](https://github.com/airbytehq/airbyte/pull/26941) | Remove `authSpecification` from spec.json, use `advanced_auth` instead                                                                                                                                                                                                                            |
| 0.4.0   | 2023-05-29 | [26720](https://github.com/airbytehq/airbyte/pull/26720) | Add Prebuilt Ad Insights reports                                                                                                                                                                                                                                                                  |
| 0.3.7   | 2023-05-12 | [26000](https://github.com/airbytehq/airbyte/pull/26000) | Handle config errors                                                                                                                                                                                                                                                                              |
| 0.3.6   | 2023-04-27 | [22999](https://github.com/airbytehq/airbyte/pull/22999) | Specified date formatting in specification                                                                                                                                                                                                                                                        |
| 0.3.5   | 2023-04-26 | [24994](https://github.com/airbytehq/airbyte/pull/24994) | Emit stream status messages                                                                                                                                                                                                                                                                       |
| 0.3.4   | 2023-04-18 | [22990](https://github.com/airbytehq/airbyte/pull/22990) | Increase pause interval                                                                                                                                                                                                                                                                           |
| 0.3.3   | 2023-04-14 | [25204](https://github.com/airbytehq/airbyte/pull/25204) | Fix data retention period validation                                                                                                                                                                                                                                                              |
| 0.3.2   | 2023-04-08 | [25003](https://github.com/airbytehq/airbyte/pull/25003) | Don't fetch `thumbnail_data_url` if it's None                                                                                                                                                                                                                                                     |
| 0.3.1   | 2023-03-27 | [24600](https://github.com/airbytehq/airbyte/pull/24600) | Reduce request record limit when retrying second page or further                                                                                                                                                                                                                                  |
| 0.3.0   | 2023-03-16 | [19141](https://github.com/airbytehq/airbyte/pull/19141) | Added Level parameter to custom Ads Insights                                                                                                                                                                                                                                                      |
| 0.2.86  | 2023-03-01 | [23625](https://github.com/airbytehq/airbyte/pull/23625) | Add user friendly fields description in spec and docs. Extend error message for invalid Account ID case.                                                                                                                                                                                          |
| 0.2.85  | 2023-02-14 | [23003](https://github.com/airbytehq/airbyte/pull/23003) | Bump facebook_business to 16.0.0                                                                                                                                                                                                                                                                  |
| 0.2.84  | 2023-01-27 | [22003](https://github.com/airbytehq/airbyte/pull/22003) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                                                                                                                                                                                                       |
| 0.2.83  | 2023-01-13 | [21149](https://github.com/airbytehq/airbyte/pull/21149) | Videos stream remove filtering                                                                                                                                                                                                                                                                    |
| 0.2.82  | 2023-01-09 | [21149](https://github.com/airbytehq/airbyte/pull/21149) | Fix AdAccount schema                                                                                                                                                                                                                                                                              |
| 0.2.81  | 2023-01-05 | [21057](https://github.com/airbytehq/airbyte/pull/21057) | Remove unsupported fields from request                                                                                                                                                                                                                                                            |
| 0.2.80  | 2022-12-21 | [20736](https://github.com/airbytehq/airbyte/pull/20736) | Fix update next cursor                                                                                                                                                                                                                                                                            |
| 0.2.79  | 2022-12-07 | [20402](https://github.com/airbytehq/airbyte/pull/20402) | Exclude Not supported fields from request                                                                                                                                                                                                                                                         |
| 0.2.78  | 2022-12-07 | [20165](https://github.com/airbytehq/airbyte/pull/20165) | Fix fields permission error                                                                                                                                                                                                                                                                       |
| 0.2.77  | 2022-12-06 | [20131](https://github.com/airbytehq/airbyte/pull/20131) | Update next cursor value at read start                                                                                                                                                                                                                                                            |
| 0.2.76  | 2022-12-03 | [20043](https://github.com/airbytehq/airbyte/pull/20043) | Allows `action_breakdowns` to be an empty list - bugfix for #20016                                                                                                                                                                                                                                |
| 0.2.75  | 2022-12-03 | [20016](https://github.com/airbytehq/airbyte/pull/20016) | Allows `action_breakdowns` to be an empty list                                                                                                                                                                                                                                                    |
| 0.2.74  | 2022-11-25 | [19803](https://github.com/airbytehq/airbyte/pull/19803) | New default for `action_breakdowns`, improve "check" command speed                                                                                                                                                                                                                                |
| 0.2.73  | 2022-11-21 | [19645](https://github.com/airbytehq/airbyte/pull/19645) | Check "breakdowns" combinations                                                                                                                                                                                                                                                                   |
| 0.2.72  | 2022-11-04 | [18971](https://github.com/airbytehq/airbyte/pull/18971) | Handle FacebookBadObjectError for empty results on async jobs                                                                                                                                                                                                                                     |
| 0.2.71  | 2022-10-31 | [18734](https://github.com/airbytehq/airbyte/pull/18734) | Reduce request record limit on retry                                                                                                                                                                                                                                                              |
| 0.2.70  | 2022-10-26 | [18045](https://github.com/airbytehq/airbyte/pull/18045) | Upgrade FB SDK to v15.0                                                                                                                                                                                                                                                                           |
| 0.2.69  | 2022-10-17 | [18045](https://github.com/airbytehq/airbyte/pull/18045) | Remove "pixel" field from the Custom Conversions stream schema                                                                                                                                                                                                                                    |
| 0.2.68  | 2022-10-12 | [17869](https://github.com/airbytehq/airbyte/pull/17869) | Remove "format" from optional datetime `end_date` field                                                                                                                                                                                                                                           |
| 0.2.67  | 2022-10-04 | [17551](https://github.com/airbytehq/airbyte/pull/17551) | Add `cursor_field` for custom_insights stream schema                                                                                                                                                                                                                                              |
| 0.2.65  | 2022-09-29 | [17371](https://github.com/airbytehq/airbyte/pull/17371) | Fix stream CustomConversions `enable_deleted=False`                                                                                                                                                                                                                                               |
| 0.2.64  | 2022-09-22 | [17304](https://github.com/airbytehq/airbyte/pull/17304) | Migrate to per-stream state.                                                                                                                                                                                                                                                                      |
| 0.2.64  | 2022-09-22 | [17027](https://github.com/airbytehq/airbyte/pull/17027) | Limit time range with 37 months when creating an insight job from lower edge object. Retry bulk request when getting error code `960`                                                                                                                                                             |
| 0.2.63  | 2022-09-06 | [15724](https://github.com/airbytehq/airbyte/pull/15724) | Add the Custom Conversion stream                                                                                                                                                                                                                                                                  |
| 0.2.62  | 2022-09-01 | [16222](https://github.com/airbytehq/airbyte/pull/16222) | Remove `end_date` from config if empty value (re-implement #16096)                                                                                                                                                                                                                                |
| 0.2.61  | 2022-08-29 | [16096](https://github.com/airbytehq/airbyte/pull/16096) | Remove `end_date` from config if empty value                                                                                                                                                                                                                                                      |
| 0.2.60  | 2022-08-19 | [15788](https://github.com/airbytehq/airbyte/pull/15788) | Retry FacebookBadObjectError                                                                                                                                                                                                                                                                      |
| 0.2.59  | 2022-08-04 | [15327](https://github.com/airbytehq/airbyte/pull/15327) | Shift date validation from config validation to stream method                                                                                                                                                                                                                                     |
| 0.2.58  | 2022-07-25 | [15012](https://github.com/airbytehq/airbyte/pull/15012) | Add `DATA_RETENTION_PERIOD`validation and fix `failed_delivery_checks` field schema type issue                                                                                                                                                                                                    |
| 0.2.57  | 2022-07-25 | [14831](https://github.com/airbytehq/airbyte/pull/14831) | Update Facebook SDK to version 14.0.0                                                                                                                                                                                                                                                             |
| 0.2.56  | 2022-07-19 | [14831](https://github.com/airbytehq/airbyte/pull/14831) | Add future `start_date` and `end_date` validation                                                                                                                                                                                                                                                 |
| 0.2.55  | 2022-07-18 | [14786](https://github.com/airbytehq/airbyte/pull/14786) | Check if the authorized user has the "MANAGE" task permission when getting the `funding_source_details` field in the ad_account stream                                                                                                                                                            |
| 0.2.54  | 2022-06-29 | [14267](https://github.com/airbytehq/airbyte/pull/14267) | Make MAX_BATCH_SIZE available in config                                                                                                                                                                                                                                                           |
| 0.2.53  | 2022-06-16 | [13623](https://github.com/airbytehq/airbyte/pull/13623) | Add fields `bid_amount` `bid_strategy` `bid_constraints` to `ads_set` stream                                                                                                                                                                                                                      |
| 0.2.52  | 2022-06-14 | [13749](https://github.com/airbytehq/airbyte/pull/13749) | Fix the `not syncing any data` issue                                                                                                                                                                                                                                                              |
| 0.2.51  | 2022-05-30 | [13317](https://github.com/airbytehq/airbyte/pull/13317) | Change tax_id to string (Canadian has letter in tax_id)                                                                                                                                                                                                                                           |
| 0.2.50  | 2022-04-27 | [12402](https://github.com/airbytehq/airbyte/pull/12402) | Add lookback window to insights streams                                                                                                                                                                                                                                                           |
| 0.2.49  | 2022-05-20 | [13047](https://github.com/airbytehq/airbyte/pull/13047) | Fix duplicating records during insights lookback period                                                                                                                                                                                                                                           |
| 0.2.48  | 2022-05-19 | [13008](https://github.com/airbytehq/airbyte/pull/13008) | Update CDK to v0.1.58 avoid crashing on incorrect stream schemas                                                                                                                                                                                                                                  |
| 0.2.47  | 2022-05-06 | [12685](https://github.com/airbytehq/airbyte/pull/12685) | Update CDK to v0.1.56 to emit an `AirbyeTraceMessage` on uncaught exceptions                                                                                                                                                                                                                      |
| 0.2.46  | 2022-04-22 | [12171](https://github.com/airbytehq/airbyte/pull/12171) | Allow configuration of page_size for requests                                                                                                                                                                                                                                                     |
| 0.2.45  | 2022-05-03 | [12390](https://github.com/airbytehq/airbyte/pull/12390) | Better retry logic for split-up async jobs                                                                                                                                                                                                                                                        |
| 0.2.44  | 2022-04-14 | [11751](https://github.com/airbytehq/airbyte/pull/11751) | Update API to a directly initialise an AdAccount with the given ID                                                                                                                                                                                                                                |
| 0.2.43  | 2022-04-13 | [11801](https://github.com/airbytehq/airbyte/pull/11801) | Fix `user_tos_accepted` schema to be an object                                                                                                                                                                                                                                                    |
| 0.2.42  | 2022-04-06 | [11761](https://github.com/airbytehq/airbyte/pull/11761) | Upgrade Facebook Python SDK to version 13                                                                                                                                                                                                                                                         |
| 0.2.41  | 2022-03-28 | [11446](https://github.com/airbytehq/airbyte/pull/11446) | Increase number of attempts for individual jobs                                                                                                                                                                                                                                                   |
| 0.2.40  | 2022-02-28 | [10698](https://github.com/airbytehq/airbyte/pull/10698) | Improve sleeps time in rate limit handler                                                                                                                                                                                                                                                         |
| 0.2.39  | 2022-03-09 | [10917](https://github.com/airbytehq/airbyte/pull/10917) | Retry connections when FB API returns error code 2 (temporary oauth error)                                                                                                                                                                                                                        |
| 0.2.38  | 2022-03-08 | [10531](https://github.com/airbytehq/airbyte/pull/10531) | Add `time_increment` parameter to custom insights                                                                                                                                                                                                                                                 |
| 0.2.37  | 2022-02-28 | [10655](https://github.com/airbytehq/airbyte/pull/10655) | Add Activities stream                                                                                                                                                                                                                                                                             |
| 0.2.36  | 2022-02-24 | [10588](https://github.com/airbytehq/airbyte/pull/10588) | Fix `execute_in_batch` for large amount of requests                                                                                                                                                                                                                                               |
| 0.2.35  | 2022-02-18 | [10348](https://github.com/airbytehq/airbyte/pull/10348) | Add error code 104 to backoff triggers                                                                                                                                                                                                                                                            |
| 0.2.34  | 2022-02-17 | [10180](https://github.com/airbytehq/airbyte/pull/9805)  | Performance and reliability fixes                                                                                                                                                                                                                                                                 |
| 0.2.33  | 2021-12-28 | [10180](https://github.com/airbytehq/airbyte/pull/10180) | Add AdAccount and Images streams                                                                                                                                                                                                                                                                  |
| 0.2.32  | 2022-01-07 | [10138](https://github.com/airbytehq/airbyte/pull/10138) | Add `primary_key` for all insights streams.                                                                                                                                                                                                                                                       |
| 0.2.31  | 2021-12-29 | [9138](https://github.com/airbytehq/airbyte/pull/9138)   | Fix videos stream format field incorrect type                                                                                                                                                                                                                                                     |
| 0.2.30  | 2021-12-20 | [8962](https://github.com/airbytehq/airbyte/pull/8962)   | Add `asset_feed_spec` field to `ad creatives` stream                                                                                                                                                                                                                                              |
| 0.2.29  | 2021-12-17 | [8649](https://github.com/airbytehq/airbyte/pull/8649)   | Retrieve ad_creatives image as data encoded                                                                                                                                                                                                                                                       |
| 0.2.28  | 2021-12-13 | [8742](https://github.com/airbytehq/airbyte/pull/8742)   | Fix for schema generation related to "breakdown" fields                                                                                                                                                                                                                                           |
| 0.2.27  | 2021-11-29 | [8257](https://github.com/airbytehq/airbyte/pull/8257)   | Add fields to Campaign stream                                                                                                                                                                                                                                                                     |
| 0.2.26  | 2021-11-19 | [7855](https://github.com/airbytehq/airbyte/pull/7855)   | Add Video stream                                                                                                                                                                                                                                                                                  |
| 0.2.25  | 2021-11-12 | [7904](https://github.com/airbytehq/airbyte/pull/7904)   | Implement retry logic for async jobs                                                                                                                                                                                                                                                              |
| 0.2.24  | 2021-11-09 | [7744](https://github.com/airbytehq/airbyte/pull/7744)   | Fix fail when async job takes too long                                                                                                                                                                                                                                                            |
| 0.2.23  | 2021-11-08 | [7734](https://github.com/airbytehq/airbyte/pull/7734)   | Resolve $ref field for discover schema                                                                                                                                                                                                                                                            |
| 0.2.22  | 2021-11-05 | [7605](https://github.com/airbytehq/airbyte/pull/7605)   | Add job retry logics to AdsInsights stream                                                                                                                                                                                                                                                        |
| 0.2.21  | 2021-10-05 | [4864](https://github.com/airbytehq/airbyte/pull/4864)   | Update insights streams with custom entries for fields, breakdowns and action_breakdowns                                                                                                                                                                                                          |
| 0.2.20  | 2021-10-04 | [6719](https://github.com/airbytehq/airbyte/pull/6719)   | Update version of facebook_business package to 12.0                                                                                                                                                                                                                                               |
| 0.2.19  | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification                                                                                                                                                                                                                         |
| 0.2.18  | 2021-09-28 | [6499](https://github.com/airbytehq/airbyte/pull/6499)   | Fix field values converting fail                                                                                                                                                                                                                                                                  |
| 0.2.17  | 2021-09-14 | [4978](https://github.com/airbytehq/airbyte/pull/4978)   | Convert values' types according to schema types                                                                                                                                                                                                                                                   |
| 0.2.16  | 2021-09-14 | [6060](https://github.com/airbytehq/airbyte/pull/6060)   | Fix schema for `ads_insights` stream                                                                                                                                                                                                                                                              |
| 0.2.15  | 2021-09-14 | [5958](https://github.com/airbytehq/airbyte/pull/5958)   | Fix url parsing and add report that exposes conversions                                                                                                                                                                                                                                           |
| 0.2.14  | 2021-07-19 | [4820](https://github.com/airbytehq/airbyte/pull/4820)   | Improve the rate limit management                                                                                                                                                                                                                                                                 |
| 0.2.12  | 2021-06-20 | [3743](https://github.com/airbytehq/airbyte/pull/3743)   | Refactor connector to use CDK: - Improve error handling. - Improve async job performance \(insights\). - Add new configuration parameter `insights_days_per_job`. - Rename stream `adsets` to `ad_sets`. - Refactor schema logic for insights, allowing to configure any possible insight stream. |
| 0.2.10  | 2021-06-16 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Update version of facebook_business to 11.0                                                                                                                                                                                                                                                       |
| 0.2.9   | 2021-06-10 | [3996](https://github.com/airbytehq/airbyte/pull/3996)   | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support                                                                                                                                                                                                                                                   |
| 0.2.8   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Add 80000 as a rate-limiting error code                                                                                                                                                                                                                                                           |
| 0.2.7   | 2021-06-03 | [3646](https://github.com/airbytehq/airbyte/pull/3646)   | Add missing fields to AdInsights streams                                                                                                                                                                                                                                                          |
| 0.2.6   | 2021-05-25 | [3525](https://github.com/airbytehq/airbyte/pull/3525)   | Fix handling call rate limit                                                                                                                                                                                                                                                                      |
| 0.2.5   | 2021-05-20 | [3396](https://github.com/airbytehq/airbyte/pull/3396)   | Allow configuring insights lookback window                                                                                                                                                                                                                                                        |
| 0.2.4   | 2021-05-13 | [3395](https://github.com/airbytehq/airbyte/pull/3395)   | Fix an issue that caused losing Insights data from the past 28 days while incremental sync                                                                                                                                                                                                        |
| 0.2.3   | 2021-04-28 | [3116](https://github.com/airbytehq/airbyte/pull/3116)   | Wait longer \(5 min\) for async jobs to start                                                                                                                                                                                                                                                     |
| 0.2.2   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726)   | Fix base connector versioning                                                                                                                                                                                                                                                                     |
| 0.2.1   | 2021-03-12 | [2391](https://github.com/airbytehq/airbyte/pull/2391)   | Support FB Marketing API v10                                                                                                                                                                                                                                                                      |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238)   | Protocol allows future/unknown properties                                                                                                                                                                                                                                                         |
| 0.1.4   | 2021-02-24 | [1902](https://github.com/airbytehq/airbyte/pull/1902)   | Add `include_deleted` option in params                                                                                                                                                                                                                                                            |
| 0.1.3   | 2021-02-15 | [1990](https://github.com/airbytehq/airbyte/pull/1990)   | Support Insights stream via async queries                                                                                                                                                                                                                                                         |
| 0.1.2   | 2021-01-22 | [1699](https://github.com/airbytehq/airbyte/pull/1699)   | Add incremental support                                                                                                                                                                                                                                                                           |
| 0.1.1   | 2021-01-15 | [1552](https://github.com/airbytehq/airbyte/pull/1552)   | Release Native Facebook Marketing Connector                                                                                                                                                                                                                                                       |

</details>
