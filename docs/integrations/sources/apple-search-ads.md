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
7. For **Start Date** and **End Date**, enter the date in YYYY-MM-DD format. For DAILY reports, the Start Date can't be
   earlier than 90 days from today. If the End Date field is left blank, Airbyte will replicate data to today.
8. When syncing large amounts of data over vast durations, you can customize **Exponential Backoff Factor** in order to
   reduce the chance of synchronization failures in case of Apple's rate limit kicking in. 
9. You can also decrease the **Lookback Window** in order to sync smaller amounts of data on each incremental sync, 
   at the cost of missing late data attributions.
10. Click **Set up source**.

## Supported sync modes

The Apple Search Ads source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- [Full Refresh - Overwrite](https://docs.airbyte.com/understanding-airbyte/glossary#full-refresh-sync)
- [Full Refresh - Append](https://docs.airbyte.com/understanding-airbyte/connections/full-refresh-append)
- [Incremental - Append](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append)
- [Incremental - Append + Deduped](https://docs.airbyte.com/understanding-airbyte/connections/incremental-append-deduped)

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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                              |
|:--------|:-----------|:---------------------------------------------------------|:-------------------------------------------------------------------------------------|
| 0.4.1 | 2025-02-22 | [54284](https://github.com/airbytehq/airbyte/pull/54284) | Update dependencies |
| 0.4.0 | 2025-02-20 | [54170](https://github.com/airbytehq/airbyte/pull/54170) | Externalize backoff factor and lookback window configurations |
| 0.3.3 | 2025-02-15 | [53920](https://github.com/airbytehq/airbyte/pull/53920) | Update dependencies |
| 0.3.2 | 2025-02-14 | [53685](https://github.com/airbytehq/airbyte/pull/53685) | Fix granularity to daily |
| 0.3.1 | 2025-02-08 | [53422](https://github.com/airbytehq/airbyte/pull/53422) | Update dependencies |
| 0.3.0 | 2025-02-03 | [53136](https://github.com/airbytehq/airbyte/pull/53136) | Update API version to V5 |
| 0.2.9 | 2025-02-01 | [52899](https://github.com/airbytehq/airbyte/pull/52899) | Update dependencies |
| 0.2.8 | 2025-01-25 | [52197](https://github.com/airbytehq/airbyte/pull/52197) | Update dependencies |
| 0.2.7 | 2025-01-18 | [51745](https://github.com/airbytehq/airbyte/pull/51745) | Update dependencies |
| 0.2.6 | 2025-01-11 | [51249](https://github.com/airbytehq/airbyte/pull/51249) | Update dependencies |
| 0.2.5 | 2024-12-28 | [50469](https://github.com/airbytehq/airbyte/pull/50469) | Update dependencies |
| 0.2.4 | 2024-12-21 | [50155](https://github.com/airbytehq/airbyte/pull/50155) | Update dependencies |
| 0.2.3 | 2024-12-14 | [49561](https://github.com/airbytehq/airbyte/pull/49561) | Update dependencies |
| 0.2.2 | 2024-12-12 | [47751](https://github.com/airbytehq/airbyte/pull/47751) | Update dependencies |
| 0.2.1 | 2024-11-08 | [48440](https://github.com/airbytehq/airbyte/pull/48440) | Set authentication grant_type to client_credentials |
| 0.2.0 | 2024-10-01 | [46288](https://github.com/airbytehq/airbyte/pull/46288) | Migrate to Manifest-only |
| 0.1.20 | 2024-09-28 | [46153](https://github.com/airbytehq/airbyte/pull/46153) | Update dependencies |
| 0.1.19 | 2024-09-21 | [45803](https://github.com/airbytehq/airbyte/pull/45803) | Update dependencies |
| 0.1.18 | 2024-09-14 | [45474](https://github.com/airbytehq/airbyte/pull/45474) | Update dependencies |
| 0.1.17 | 2024-09-07 | [45326](https://github.com/airbytehq/airbyte/pull/45326) | Update dependencies |
| 0.1.16 | 2024-08-31 | [45013](https://github.com/airbytehq/airbyte/pull/45013) | Update dependencies |
| 0.1.15 | 2024-08-24 | [44654](https://github.com/airbytehq/airbyte/pull/44654) | Update dependencies |
| 0.1.14 | 2024-08-17 | [44322](https://github.com/airbytehq/airbyte/pull/44322) | Update dependencies |
| 0.1.13 | 2024-08-12 | [43912](https://github.com/airbytehq/airbyte/pull/43912) | Update dependencies |
| 0.1.12 | 2024-08-10 | [43514](https://github.com/airbytehq/airbyte/pull/43514) | Update dependencies |
| 0.1.11 | 2024-08-03 | [43195](https://github.com/airbytehq/airbyte/pull/43195) | Update dependencies |
| 0.1.10 | 2024-07-27 | [42660](https://github.com/airbytehq/airbyte/pull/42660) | Update dependencies |
| 0.1.9 | 2024-07-20 | [42225](https://github.com/airbytehq/airbyte/pull/42225) | Update dependencies |
| 0.1.8 | 2024-07-13 | [41722](https://github.com/airbytehq/airbyte/pull/41722) | Update dependencies |
| 0.1.7 | 2024-07-10 | [41546](https://github.com/airbytehq/airbyte/pull/41546) | Update dependencies |
| 0.1.6 | 2024-07-09 | [40832](https://github.com/airbytehq/airbyte/pull/40832) | Update dependencies |
| 0.1.5 | 2024-06-25 | [40364](https://github.com/airbytehq/airbyte/pull/40364) | Update dependencies |
| 0.1.4 | 2024-06-22 | [40186](https://github.com/airbytehq/airbyte/pull/40186) | Update dependencies |
| 0.1.3 | 2024-06-04 | [38967](https://github.com/airbytehq/airbyte/pull/38967) | [autopull] Upgrade base image to v1.2.1 |
| 0.1.2 | 2024-05-21 | [38502](https://github.com/airbytehq/airbyte/pull/38502) | [autopull] base image + poetry + up_to_date |
| 0.1.1 | 2023-07-11 | [28153](https://github.com/airbytehq/airbyte/pull/28153) | Fix manifest duplicate key (no change in behavior for the syncs) |
| 0.1.0 | 2022-11-17 | [19557](https://github.com/airbytehq/airbyte/pull/19557) | Initial release with campaigns, adgroups & keywords streams (base and daily reports) |

</details>
