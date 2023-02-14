# Facebook Marketing

This page guides you through the process of setting up the Facebook Marketing source connector.

## Prerequisites

* A [Facebook Ad Account ID](https://www.facebook.com/business/help/1492627900875762)
<!-- env:oss -->
* (For Open Source) A [Facebook App](https://developers.facebook.com/apps/) with the Marketing API enabled
<!-- /env:oss -->

## Setup guide

<!-- env:cloud -->
**For Airbyte Cloud:**

To set up Facebook Marketing as a source in Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. On the Set up the source page, select **Facebook Marketing** from the **Source type** dropdown.
4. For Name, enter a name for the Facebook Marketing connector.
5. Click **Authenticate your account** to authorize your [Meta for Developers](https://developers.facebook.com/) account. Airbyte will authenticate the account you are already logged in to. Make sure you are logged into the right account.
6. For **Start Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.

    :::warning
    Insight tables are only able to pull data from 37 months. If you are syncing insight tables and your start date is older than 37 months, your sync will fail.
    :::

7. For **End Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and before this date will be replicated. If this field is blank, Airbyte will replicate the latest data.
8. For Account ID, enter your [Facebook Ad Account ID Number](https://www.facebook.com/business/help/1492627900875762).
9. (Optional) Toggle the **Include Deleted** button to include data from deleted Campaigns, Ads, and AdSets.

    :::info
    The Facebook Marketing API does not have a concept of deleting records in the same way that a database does. While you can archive or delete an ad campaign, the API maintains a record of the campaign. Toggling the **Include Deleted** button lets you replicate records for campaigns or ads even if they were archived or deleted from the Facebook platform.
    :::

10. (Optional) Toggle the **Fetch Thumbnail Images** button to fetch the `thumbnail_url` and store the result in `thumbnail_data_url` for each [Ad Creative](https://developers.facebook.com/docs/marketing-api/creative/).
11. (Optional) In the Custom Insights section, click **Add**.
    To retrieve specific fields from Facebook Ads Insights combined with other breakdowns, you can choose which fields and breakdowns to sync.

    :::warning
    Additional streams for Facebook Marketing are dynamically created based on the specified Custom Insights. For an existing Facebook Marketing source, when you are updating or removing Custom Insights, you should also ensure that any connections syncing to these streams are either disabled or have had their source schema refreshed.
    :::

    We recommend following the Facebook Marketing [documentation](https://developers.facebook.com/docs/marketing-api/insights/breakdowns) to understand the breakdown limitations. Some fields can not be requested and many others only work when combined with specific fields. For example, the breakdown `app_id` is only supported with the `total_postbacks` field.

    To configure Custom Insights:

    1. For **Name**, enter a name for the insight. This will be used as the Airbyte stream name
    2. For **Fields**, enter a list of the fields you want to pull from the Facebook Marketing API.
    3. For **End Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and before this date will be replicated. If this field is blank, Airbyte will replicate the latest data.
    4. For **Breakdowns**, enter a list of the breakdowns you want to configure.
    5. For **Start Date**, enter the date in the `YYYY-MM-DDTHH:mm:ssZ` format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
    6. For **Time Increment**, enter the number of days over which you want to aggregate statistics.

            For example, if you set this value to 7, Airbyte will report statistics as 7-day aggregates starting from the Start Date. Suppose the start and end dates are October 1st and October 30th, then the connector will output 5 records: 01 - 06, 07 - 13, 14 - 20, 21 - 27, and 28 - 30 (3 days only).  
    7. For **Action Breakdown**, enter a list of the action breakdowns you want to configure.
    8. For **Custom Insights Lookback Window**, fill in the appropriate value. See [more](#facebook-marketing-attribution-reporting) on this parameter.
    9. Click **Done**.
12. For **Page Size of Requests**, fill in the size of the page in case pagintion kicks in. Feel free to ignore it, the default value should work in most cases.
13. For **Insights Lookback Window**, fill in the appropriate value. See [more](#facebook-marketing-attribution-reporting) on this parameter.
14. Click **Set up source**.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

To set up Facebook Marketing as a source in Airbyte Open Source:

1. Navigate to [Meta for Developers](https://developers.facebook.com/apps/) and [create an app](https://developers.facebook.com/docs/development/create-an-app/) with the app type Business.
2. From your App’s dashboard, [setup the Marketing API](https://developers.facebook.com/docs/marketing-apis/get-started).
3. Generate a Marketing API access token: From your App’s Dashboard, click **Marketing API** --> **Tools**. Select all the available token permissions (`ads_management`, `ads_read`, `read_insights`, `business_management`) and click **Get token**. Copy the generated token for later use.
4. Request a rate increase limit: Facebook [heavily throttles](https://developers.facebook.com/docs/marketing-api/overview/authorization#limits) API tokens generated from Facebook Apps with the "Standard Access" tier (the default tier for new apps), making it infeasible to use the token for syncs with Airbyte. You'll need to request an upgrade to Advanced Access for your app on the following permissions:

    * Ads Management Standard Access
    * ads_read
    * Ads_management

    See the Facebook [documentation on Authorization](https://developers.facebook.com/docs/marketing-api/overview/authorization/#access-levels) to request Advanced Access to the relevant permissions.
5. Navigate to the Airbyte Open Source Dashboard. Add the access token when prompted to do so and follow the same instructions as for [setting up the Facebook Connector on Airbyte Cloud](#for-airbyte-cloud).
<!-- /env:oss -->

## Supported sync modes

The Facebook Marketing source connector supports the following sync modes:

* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental Sync - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append) (except for the AdCreatives and AdAccount tables)
* [Incremental Sync - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history) (except for the AdCreatives and AdAccount tables)

## Supported tables

You can replicate the following tables using the Facebook Marketing connector:

* [Activities](https://developers.facebook.com/docs/marketing-api/reference/ad-activity)
* [AdAccount](https://developers.facebook.com/docs/marketing-api/reference/ad-account)
* [AdCreatives](https://developers.facebook.com/docs/marketing-api/reference/ad-creative#fields)
* [AdSets](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign#fields)
* [Ads](https://developers.facebook.com/docs/marketing-api/reference/adgroup#fields)
* [AdInsights](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)
* [Campaigns](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign-group#fields)
* [CustomConversions](https://developers.facebook.com/docs/marketing-api/reference/custom-conversion)
* [Images](https://developers.facebook.com/docs/marketing-api/reference/ad-image)
* [Videos](https://developers.facebook.com/docs/marketing-api/reference/video)

You can segment the AdInsights table into parts based on the following information. Each part will be synced as a separate table if normalization is enabled:

* Country
* DMA (Designated Market Area)
* Gender & Age
* Platform & Device
* Region

For more information, see the [Facebook Insights API documentation.](https://developers.facebook.com/docs/marketing-api/reference/adgroup/insights/)
Pay attention, that not all fields (e.g. conversions, conversion_values) will be returned for AdInsights, see [docs](https://developers.facebook.com/docs/marketing-api/reference/ads-action-stats/).
To get all fields You should use custom insights with **breakdowns**.

## Facebook Marketing Attribution Reporting
Please be informed that the connector uses the `lookback_window` parameter to perform the repetitive read of the last `<lookback_window>` days in the Incremental sync mode. This means some data will be synced twice (or possibly more often) despite the cursor value being up-to-date. You can change this date window by modifying the `lookback_window` parameter when setting up the source. The smaller the value - the fewer duplicates you will have. The greater the value - the more precise results you will get. More details on what the attribution window is and what purpose it serves can be found in this [Facebook Article](https://www.facebook.com/business/help/458681590974355?id=768381033531365).

## Data type mapping

| Integration Type | Airbyte Type |
| :--------------: | :----------: |
|      string      |    string    |
|      number      |    number    |
|      array       |    array     |
|      object      |    object    |

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                                                                                                                                                                                                                           |
|:--------|:-----------|:---------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0.2.84  | 2023-01-27 | [22003](https://github.com/airbytehq/airbyte/pull/22003) | Set `AvailabilityStrategy` for streams explicitly to `None`                                                     ||         |            |                                                          |                                                                                                                                                                                                                                                                                                   |
| 0.2.83  | 2023-01-13 | [21149](https://github.com/airbytehq/airbyte/pull/21149) | Videos stream remove filtering                                                                                                                                                                                                                                                                    |
| 0.2.82  | 2023-01-09 | [21149](https://github.com/airbytehq/airbyte/pull/21149) | Fix AdAccount schema                                                                                                                                                                                                                                                                              |
| 0.2.81  | 2023-01-05 | [21057](https://github.com/airbytehq/airbyte/pull/21057) | Remove unsupported fields from request                                                                                                                                                                                                                                                            |
| 0.2.80  | 2022-12-21 | [20736](https://github.com/airbytehq/airbyte/pull/20736) | Fix update next cursor                                                                                                                                                                                                                                                                            |
| 0.2.79  | 2022-12-07 | [20402](https://github.com/airbytehq/airbyte/pull/20402) | Exclude Not supported fields from request                                                                                                                                                                                                                                                         |
| 0.2.78  | 2022-12-07 | [20165](https://github.com/airbytehq/airbyte/pull/20165) | fix fields permission error                                                                                                                                                                                                                                                                       |
| 0.2.77  | 2022-12-06 | [20131](https://github.com/airbytehq/airbyte/pull/20131) | update next cursor value at read start                                                                                                                                                                                                                                                            |
| 0.2.76  | 2022-12-03 | [20043](https://github.com/airbytehq/airbyte/pull/20043) | Allows `action_breakdowns` to be an empty list - bugfix for #20016                                                                                                                                                                                                                                |
| 0.2.75  | 2022-12-03 | [20016](https://github.com/airbytehq/airbyte/pull/20016) | Allows `action_breakdowns` to be an empty list                                                                                                                                                                                                                                                    |
| 0.2.74  | 2022-11-25 | [19803](https://github.com/airbytehq/airbyte/pull/19803) | New default for `action_breakdowns`, improve "check" command speed                                                                                                                                                                                                                                |
| 0.2.73  | 2022-11-21 | [19645](https://github.com/airbytehq/airbyte/pull/19645) | Check "breakdowns" combinations                                                                                                                                                                                                                                                                   |
| 0.2.72  | 2022-11-04 | [18971](https://github.com/airbytehq/airbyte/pull/18971) | handle FacebookBadObjectError for empty results on async jobs                                                                                                                                                                                                                                     |
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
| 0.2.55  | 2022-07-18 | [14786](https://github.com/airbytehq/airbyte/pull/14786) | Check if the authorized user has the "MANAGE" task permission when getting the `funding_source_details` field in the ad\_account stream                                                                                                                                                           |
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
| 0.2.20  | 2021-10-04 | [6719](https://github.com/airbytehq/airbyte/pull/6719)   | Update version of facebook\_business package to 12.0                                                                                                                                                                                                                                              |
| 0.2.19  | 2021-09-30 | [6438](https://github.com/airbytehq/airbyte/pull/6438)   | Annotate Oauth2 flow initialization parameters in connector specification                                                                                                                                                                                                                         |
| 0.2.18  | 2021-09-28 | [6499](https://github.com/airbytehq/airbyte/pull/6499)   | Fix field values converting fail                                                                                                                                                                                                                                                                  |
| 0.2.17  | 2021-09-14 | [4978](https://github.com/airbytehq/airbyte/pull/4978)   | Convert values' types according to schema types                                                                                                                                                                                                                                                   |
| 0.2.16  | 2021-09-14 | [6060](https://github.com/airbytehq/airbyte/pull/6060)   | Fix schema for `ads_insights` stream                                                                                                                                                                                                                                                              |
| 0.2.15  | 2021-09-14 | [5958](https://github.com/airbytehq/airbyte/pull/5958)   | Fix url parsing and add report that exposes conversions                                                                                                                                                                                                                                           |
| 0.2.14  | 2021-07-19 | [4820](https://github.com/airbytehq/airbyte/pull/4820)   | Improve the rate limit management                                                                                                                                                                                                                                                                 |
| 0.2.12  | 2021-06-20 | [3743](https://github.com/airbytehq/airbyte/pull/3743)   | Refactor connector to use CDK: - Improve error handling. - Improve async job performance \(insights\). - Add new configuration parameter `insights_days_per_job`. - Rename stream `adsets` to `ad_sets`. - Refactor schema logic for insights, allowing to configure any possible insight stream. |
| 0.2.10  | 2021-06-16 | [3973](https://github.com/airbytehq/airbyte/pull/3973)   | Update version of facebook\_business to 11.0                                                                                                                                                                                                                                                      |
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
