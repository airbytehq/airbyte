# Apple Search Ads
This page contains the setup guide and reference information for the Apple Search Ads source connector.

## Setup guide
### Step 1: Set up Apple Search Ads
1. With an administrator account, [create an API user role](https://developer.apple.com/documentation/apple_search_ads/implementing_oauth_for_the_apple_search_ads_api) from the Apple Search Ads UI.
2. Then [implement OAuth for your API user](https://developer.apple.com/documentation/apple_search_ads/implementing_oauth_for_the_apple_search_ads_api) in order to the required Client Secret and Client Id.


### Step 2: Set up the source connector in Airbyte
#### For Airbyte Open Source
1. Log in to your Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Apple Search Ads** from the **Source type** dropdown.
4. Enter a name for your source.
5. For **Org Id**, enter the Id of your organization (found in the Apple Search Ads UI).
6. Enter the **Client ID** and the **Client Secret** from [Step 1](#step-1-set-up-apple-search-ads).
7. For **Start Date** and **End Date**, enter the date in YYYY-MM-DD format. For DAILY reports, the Start Date can't be earlier than 90 days from today. If the End Date field is left blank, Airbyte will replicate data to today.
8. Click **Set up source**.

## Supported sync modes
The Apple Search Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
* [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
* [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
* [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
* [Incremental - Deduped History](https://docs.airbyte.com/understanding-airbyte/connections/incremental-deduped-history)

## Supported Streams
The Apple Ads source connector supports the following streams. For more information, see the [Apple Search Ads API](https://developer.apple.com/documentation/apple_search_ads).

### Base streams
- [campaigns](https://developer.apple.com/documentation/apple_search_ads/get_all_campaigns)
- [adgroups](https://developer.apple.com/documentation/apple_search_ads/get_all_ad_groups)
- [keywords](https://developer.apple.com/documentation/apple_search_ads/get_all_targeting_keywords_in_an_ad_group)

### Report Streams
- [campaigns_report_daily](https://developer.apple.com/documentation/apple_search_ads/get_campaign-level_reports)
- [adgroups_report_daily](https://developer.apple.com/documentation/apple_search_ads/get__ad_group-level_reports)
- [keywords_report_daily](https://developer.apple.com/documentation/apple_search_ads/get_keyword-level_reports)

### Report aggregation
The Apple Search Ads currently offers [aggregation](https://developer.apple.com/documentation/apple_search_ads/reportingrequest) at hourly, daily, weekly, or monthly level.

However, at this moment and as indicated in the stream names, the connector only offers data with daily aggregation.


## Changelog
| Version | Date       | Pull Request                                            | Subject                                                                              |
|:--------|:-----------|:--------------------------------------------------------|:-------------------------------------------------------------------------------------|
| 0.1.1   | 2023-07-11 | [28153](https://github.com/airbytehq/airbyte/pull/28153) | Fix manifest duplicate key (no change in behavior for the syncs)                     |
| 0.1.0   | 2022-11-17 | [19557](https://github.com/airbytehq/airbyte/pull/19557) | Initial release with campaigns, adgroups & keywords streams (base and daily reports) |
