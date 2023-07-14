# TikTok Marketing

This page guides you through the process of setting up the TikTok Marketing source connector.

## Prerequisites

<!-- env:cloud -->
**For Airbyte Cloud:**

* A Tiktok Ads Business account with permission to access data from accounts you want to sync
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**
For the Production environment:
* Access token
* Secret
* App ID

To access the Sandbox environment:
* Access token
* Advertiser ID
<!-- /env:oss -->

## Setup guide

### Step 1: Set up TikTok

1. Create a TikTok For Business account: [Link](https://ads.tiktok.com/marketing_api/docs?rid=fgvgaumno25&id=1702715936951297)
2. (Open source only) Create developer application: [Link](https://ads.tiktok.com/marketing_api/docs?rid=fgvgaumno25&id=1702716474845185)
3. (Open source only) For a sandbox environment: create a Sandbox Ad Account [Link](https://ads.tiktok.com/marketing_api/docs?rid=fgvgaumno25&id=1701890920013825)

### Step 2: Set up the source connector in Airbyte

<!-- env:cloud -->
**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the source setup page, select **Tiktok Marketing** from the Source type dropdown and enter a name for this connector.
4. Select `OAuth2.0` Authorization method, then click `Authenticate your account`.
5. Log in and Authorize to the Tiktok account
6. Choose required Start date
7. click `Set up source`.
<!-- /env:cloud -->

<!-- env:oss -->
**For Airbyte Open Source:**

1. Go to local Airbyte page.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**.
3. On the Set up the source page, enter the name for the connector and select **Tiktok Marketing** from the Source type dropdown.
4. Select `Production Access Token` or `Sandbox Access Token` Authorization method, then copy and paste info from step 1.
5. Choose required Start date
6. Click `Set up source`.
<!-- /env:oss -->

## Supported streams and sync modes

| Stream                                    | Environment  | Key                                        | Incremental |
|:------------------------------------------|--------------|--------------------------------------------|:------------|
| Advertisers                               | Prod,Sandbox | advertiser_id                              | No          |
| AdGroups                                  | Prod,Sandbox | adgroup_id                                 | Yes         |
| Ads                                       | Prod,Sandbox | ad_id                                      | Yes         |
| Campaigns                                 | Prod,Sandbox | campaign_id                                | Yes         |
| AdsReportsHourly                          | Prod,Sandbox | ad_id, stat_time_hour                      | Yes         |
| AdsReportsDaily                           | Prod,Sandbox | ad_id, stat_time_day                       | Yes         |
| AdsReportsLifetime                        | Prod,Sandbox | ad_id                                      | No          |
| AdvertisersReportsHourly                  | Prod         | advertiser_id, stat_time_hour              | Yes         |
| AdvertisersReportsDaily                   | Prod         | advertiser_id, stat_time_day               | Yes         |
| AdvertisersReportsLifetime                | Prod         | advertiser_id                              | No          |
| AdGroupsReportsHourly                     | Prod,Sandbox | adgroup_id, stat_time_hour                 | Yes         |
| AdGroupsReportsDaily                      | Prod,Sandbox | adgroup_id, stat_time_day                  | Yes         |
| AdGroupsReportsLifetime                   | Prod,Sandbox | adgroup_id                                 | No          |
| CampaignsReportsHourly                    | Prod,Sandbox | campaign_id, stat_time_hour                | Yes         |
| CampaignsReportsDaily                     | Prod,Sandbox | campaign_id, stat_time_day                 | Yes         |
| CampaignsReportsLifetime                  | Prod,Sandbox | campaign_id                                | No          |
| AdvertisersAudienceReportsDaily           | Prod         | advertiser_id, stat_time_day, gender, age  | Yes         |
| AdvertisersAudienceReportsByCountryDaily  | Prod         | advertiser_id, stat_time_day, country_code | Yes         |
| AdvertisersAudienceReportsByPlatformDaily | Prod         | advertiser_id, stat_time_day, platform     | Yes         |
| AdvertisersAudienceReportsLifetime        | Prod         | advertiser_id, gender, age                 | No          |
| AdGroupAudienceReportsDaily               | Prod,Sandbox | adgroup_id, stat_time_day, gender, age     | Yes         |
| AdGroupAudienceReportsByCountryDaily      | Prod,Sandbox | adgroup_id, stat_time_day, country_code    | Yes         |
| AdGroupAudienceReportsByPlatformDaily     | Prod,Sandbox | adgroup_id, stat_time_day, platform        | Yes         |
| AdsAudienceReportsDaily                   | Prod,Sandbox | ad_id, stat_time_day, gender, age          | Yes         |
| AdsAudienceReportsByCountryDaily          | Prod,Sandbox | ad_id, stat_time_day, country_code         | Yes         |
| AdsAudienceReportsByPlatformDaily         | Prod,Sandbox | ad_id, stat_time_day, platform             | Yes         |
| CampaignsAudienceReportsDaily             | Prod,Sandbox | campaign_id, stat_time_day, gender, age    | Yes         |
| CampaignsAudienceReportsByCountryDaily    | Prod,Sandbox | campaign_id, stat_time_day, country_code   | Yes         |
| CampaignsAudienceReportsByPlatformDaily   | Prod,Sandbox | campaign_id, stat_time_day, platform       | Yes         |

:::info

TikTok Reporting API has some [Data Latency](https://ads.tiktok.com/marketing_api/docs?id=1738864894606337), usually of about 11 hours.
It is recommended to use higher values of attribution window (used in Incremental Syncs), at least 3 days, to ensure that the connector updates metrics in already presented records.

:::

### Report Aggregation
Reports synced by this connector can use either hourly, daily, or lifetime granularities for aggregating performance data. For example, if you select the daily-aggregation flavor of a report, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.

### Output Schemas
**[Advertisers](https://ads.tiktok.com/marketing_api/docs?id=1708503202263042) Stream**
```
{
  "contacter": "Ai***te",
  "phonenumber": "+13*****5753",
  "license_no": "",
  "promotion_center_city": null,
  "balance": 10,
  "license_url": null,
  "timezone": "Etc/GMT+8",
  "reason": "",
  "telephone": "+14*****6785",
  "id": 7002238017842757633,
  "language": "en",
  "country": "US",
  "role": "ROLE_ADVERTISER",
  "license_province": null,
  "display_timezone": "America/Los_Angeles",
  "email": "i***************@**********",
  "license_city": null,
  "industry": "291905",
  "create_time": 1630335591,
  "promotion_center_province": null,
  "address": "350 29th avenue, San Francisco",
  "currency": "USD",
  "promotion_area": "0",
  "status": "STATUS_ENABLE",
  "description": "https://",
  "brand": null,
  "name": "Airbyte0830",
  "company": "Airbyte"
}
```

**[AdGroups](https://ads.tiktok.com/marketing_api/docs?id=1708503489590273) Stream**
```
{
  "placement_type": "PLACEMENT_TYPE_AUTOMATIC",
  "budget": 20,
  "budget_mode": "BUDGET_MODE_DAY",
  "display_mode": null,
  "schedule_infos": null,
  "billing_event": "CPC",
  "conversion_window": null,
  "adgroup_name": "Ad Group20211020010107",
  "interest_keywords": [],
  "is_comment_disable": 0,
  "rf_buy_type": null,
  "frequency": null,
  "bid_type": "BID_TYPE_NO_BID",
  "placement": null,
  "bid": 0,
  "include_custom_actions": [],
  "operation_system": [],
  "pixel_id": null,
  "dayparting": "111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
  "app_type": null,
  "conversion_id": 0,
  "rf_predict_cpr": null,
  "deep_bid_type": null,
  "scheduled_budget": 0.0,
  "adgroup_id": 1714125049901106,
  "frequency_schedule": null,
  "exclude_custom_actions": [],
  "advertiser_id": 7002238017842757633,
  "deep_cpabid": 0,
  "is_new_structure": true,
  "buy_impression": null,
  "external_type": "WEBSITE",
  "excluded_audience": [],
  "deep_external_action": null,
  "interest_category_v2": [],
  "rf_predict_frequency": null,
  "audience": [],
  "pacing": "PACING_MODE_SMOOTH",
  "brand_safety_partner": null,
  "daily_retention_ratio": null,
  "optimize_goal": "CLICK",
  "enable_search_result": false,
  "conversion_bid": 0,
  "schedule_end_time": "2021-10-31 09:01:07",
  "opt_status": "ENABLE",
  "status": "ADGROUP_STATUS_CAMPAIGN_DISABLE",
  "app_id": null,
  "external_action": null,
  "schedule_type": "SCHEDULE_START_END",
  "brand_safety": "NO_BRAND_SAFETY",
  "campaign_id": 1714125042508817,
  "campaign_name": "Website Traffic20211020010104",
  "split_test_adgroup_ids": [],
  "action_v2": [],
  "is_hfss": false,
  "keywords": null,
  "create_time": "2021-10-20 08:04:05",
  "feed_type": null,
  "languages": ["en"],
  "enable_inventory_filter": false,
  "device_price": [],
  "location": [6252001],
  "schedule_start_time": "2021-10-20 09:01:07",
  "skip_learning_phase": 0,
  "gender": "GENDER_UNLIMITED",
  "creative_material_mode": "CUSTOM",
  "app_download_url": null,
  "device_models": [],
  "automated_targeting": "OFF",
  "connection_type": [],
  "ios14_quota_type": "UNOCCUPIED",
  "modify_time": "2022-03-24 12:06:54",
  "category": 0,
  "statistic_type": null,
  "video_download": "ALLOW_DOWNLOAD",
  "age": ["AGE_25_34", "AGE_35_44", "AGE_45_54"],
  "buy_reach": null,
  "is_share_disable": false
}
```

**[Ads](https://ads.tiktok.com/marketing_api/docs?id=1708572923161602) Stream**
```
{
  "vast_moat": false,
  "is_new_structure": true,
  "campaign_name": "CampaignVadimTraffic",
  "landing_page_urls": null,
  "card_id": null,
  "adgroup_id": 1728545385226289,
  "campaign_id": 1728545382536225,
  "status": "AD_STATUS_CAMPAIGN_DISABLE",
  "brand_safety_postbid_partner": "UNSET",
  "advertiser_id": 7002238017842757633,
  "is_aco": false,
  "ad_text": "Open-source\ndata integration for modern data teams",
  "identity_id": "7080121820963422209",
  "display_name": "airbyte",
  "open_url": "",
  "external_action": null,
  "playable_url": "",
  "create_time": "2022-03-28 12:09:09",
  "product_ids": [],
  "adgroup_name": "AdGroupVadim",
  "fallback_type": "UNSET",
  "creative_type": null,
  "ad_name": "AdVadim-Optimized Version 3_202203281449_2022-03-28 05:03:44",
  "video_id": "v10033g50000c90q1d3c77ub6e96fvo0",
  "ad_format": "SINGLE_VIDEO",
  "profile_image": "https://p21-ad-sg.ibyteimg.com/large/ad-site-i18n-sg/202203285d0de5c114d0690a462bb6a4",
  "open_url_type": "NORMAL",
  "click_tracking_url": null,
  "page_id": null,
  "ad_texts": null,
  "landing_page_url": "https://airbyte.com",
  "identity_type": "CUSTOMIZED_USER",
  "avatar_icon_web_uri": "ad-site-i18n-sg/202203285d0de5c114d0690a462bb6a4",
  "app_name": "",
  "modify_time": "2022-03-28 21:34:26",
  "opt_status": "ENABLE",
  "call_to_action_id": "7080120957230238722",
  "image_ids": ["v0201/7f371ff6f0764f8b8ef4f37d7b980d50"],
  "ad_id": 1728545390695442,
  "impression_tracking_url": null,
  "is_creative_authorized": false
}
```

**[Campaigns](https://ads.tiktok.com/marketing_api/docs?id=1708582970809346) Stream**
```
{
  "create_time": "2021-10-19 18:18:08",
  "campaign_id": 1714073078669329,
  "roas_bid": 0.0,
  "advertiser_id": 7002238017842757633,
  "modify_time": "2022-03-28 12:01:56",
  "campaign_type": "REGULAR_CAMPAIGN",
  "status": "CAMPAIGN_STATUS_DISABLE",
  "objective_type": "TRAFFIC",
  "split_test_variable": null,
  "opt_status": "DISABLE",
  "budget": 50,
  "is_new_structure": true,
  "deep_bid_type": null,
  "campaign_name": "Website Traffic20211019110444",
  "budget_mode": "BUDGET_MODE_DAY",
  "objective": "LANDING_PAGE"
}
```

**AdsReportsDaily Stream - [BasicReports](https://ads.tiktok.com/marketing_api/docs?id=1707957200780290)**
```
{
  "dimensions": {
    "ad_id": 1728545390695442,
    "stat_time_day": "2022-03-29 00:00:00"
  },
  "metrics": {
    "real_time_result_rate": 0.93,
    "campaign_id": 1728545382536225,
    "placement": "Automatic Placement",
    "frequency": 1.17,
    "cpc": 0.35,
    "ctr": 0.93,
    "cost_per_result": 0.3509,
    "impressions": 6137,
    "cost_per_conversion": 0,
    "real_time_result": 57,
    "adgroup_id": 1728545385226289,
    "result_rate": 0.93,
    "cost_per_1000_reached": 3.801,
    "ad_text": "Open-source\ndata integration for modern data teams",
    "spend": 20,
    "conversion_rate": 0,
    "real_time_cost_per_conversion": 0,
    "promotion_type": "Website",
    "tt_app_id": 0,
    "real_time_cost_per_result": 0.3509,
    "conversion": 0,
    "secondary_goal_result": null,
    "campaign_name": "CampaignVadimTraffic",
    "cpm": 3.26,
    "result": 57,
    "ad_name": "AdVadim-Optimized Version 3_202203281449_2022-03-28 05:03:44",
    "secondary_goal_result_rate": null,
    "clicks": 57,
    "reach": 5262,
    "cost_per_secondary_goal_result": null,
    "real_time_conversion": 0,
    "real_time_conversion_rate": 0,
    "mobile_app_id": "0",
    "tt_app_name": "0",
    "adgroup_name": "AdGroupVadim",
    "dpa_target_audience_type": null
  }
}
```

**AdvertisersReportsDaily Stream - [BasicReports](https://ads.tiktok.com/marketing_api/docs?id=1707957200780290)**
```
{
  "metrics": {
    "cpm": 5.43,
    "impressions": 3682,
    "frequency": 1.17,
    "reach": 3156,
    "cash_spend": 20,
    "ctr": 1.14,
    "spend": 20,
    "cpc": 0.48,
    "cost_per_1000_reached": 6.337,
    "clicks": 42,
    "voucher_spend": 0
  },
  "dimensions": {
    "stat_time_day": "2022-03-30 00:00:00",
    "advertiser_id": 7002238017842757633
  }
}

```

**AdGroupsReportsDaily Stream - [BasicReports](https://ads.tiktok.com/marketing_api/docs?id=1707957200780290)**
```
{
  "metrics": {
    "real_time_conversion": 0,
    "real_time_cost_per_conversion": 0,
    "cost_per_1000_reached": 3.801,
    "mobile_app_id": "0",
    "reach": 5262,
    "cpm": 3.26,
    "conversion": 0,
    "promotion_type": "Website",
    "clicks": 57,
    "real_time_result_rate": 0.93,
    "real_time_conversion_rate": 0,
    "cost_per_conversion": 0,
    "dpa_target_audience_type": null,
    "result": 57,
    "cpc": 0.35,
    "impressions": 6137,
    "cost_per_result": 0.3509,
    "tt_app_id": 0,
    "cost_per_secondary_goal_result": null,
    "frequency": 1.17,
    "spend": 20,
    "secondary_goal_result_rate": null,
    "real_time_cost_per_result": 0.3509,
    "real_time_result": 57,
    "placement": "Automatic Placement",
    "result_rate": 0.93,
    "tt_app_name": "0",
    "campaign_name": "CampaignVadimTraffic",
    "secondary_goal_result": null,
    "campaign_id": 1728545382536225,
    "conversion_rate": 0,
    "ctr": 0.93,
    "adgroup_name": "AdGroupVadim"
  },
  "dimensions": {
    "adgroup_id": 1728545385226289,
    "stat_time_day": "2022-03-29 00:00:00"
  }
}
```

**CampaignsReportsDaily Stream - [BasicReports](https://ads.tiktok.com/marketing_api/docs?id=1707957200780290)**
```
{
  "metrics": {
    "cpc": 0.43,
    "spend": 20,
    "clicks": 46,
    "cost_per_1000_reached": 4.002,
    "impressions": 5870,
    "ctr": 0.78,
    "frequency": 1.17,
    "cpm": 3.41,
    "campaign_name": "CampaignVadimTraffic",
    "reach": 4997
  },
  "dimensions": {
    "campaign_id": 1728545382536225,
    "stat_time_day": "2022-03-28 00:00:00"
  }
}

```

**AdsAudienceReportsDaily Stream - [AudienceReports](https://ads.tiktok.com/marketing_api/docs?id=1707957217727489)**
```
{
  {
    "result": 17,
    "clicks": 17,
    "real_time_conversion_rate": 0,
    "adgroup_id": 1728545385226289,
    "cpm": 3.01,
    "cost_per_result": 0.4165,
    "real_time_cost_per_result": 0.4165,
    "mobile_app_id": 0,
    "spend": 7.08,
    "cpc": 0.42,
    "placement": "Automatic Placement",
    "real_time_conversion": 0,
    "dpa_target_audience_type": null,
    "real_time_result_rate": 0.72,
    "adgroup_name": "AdGroupVadim",
    "tt_app_id": 0,
    "ctr": 0.72,
    "ad_text": "Open-source\ndata integration for modern data teams",
    "result_rate": 0.72,
    "ad_name": "AdVadim-Optimized Version 3_202203281449_2022-03-28 05:03:44",
    "conversion_rate": 0,
    "real_time_result": 17,
    "tt_app_name": "0",
    "cost_per_conversion": 0,
    "real_time_cost_per_conversion": 0,
    "conversion": 0,
    "impressions": 2350,
    "promotion_type": "Website",
    "campaign_id": 1728545382536225,
    "campaign_name": "CampaignVadimTraffic"
  },
  "dimensions": {
    "gender": "MALE",
    "age": "AGE_25_34",
    "ad_id": 1728545390695442,
    "stat_time_day": "2022-03-28 00:00:00"
  }
}
```

**AdvertisersAudienceReportsDaily Stream - [AudienceReports](https://ads.tiktok.com/marketing_api/docs?id=1707957217727489)**
```
{
  "dimensions": {
    "stat_time_day": "2022-03-28 00:00:00",
    "gender": "FEMALE",
    "advertiser_id": 7002238017842757633,
    "age": "AGE_35_44"
  },
  "metrics": {
    "spend": 3.09,
    "ctr": 0.93,
    "cpc": 0.44,
    "clicks": 7,
    "cpm": 4.11,
    "impressions": 752
  }
}
```

**AdGroupAudienceReportsDaily Stream - [AudienceReports](https://ads.tiktok.com/marketing_api/docs?id=1707957217727489)**
```
{
  "dimensions": {
    "gender": "MALE",
    "age": "AGE_25_34",
    "stat_time_day": "2022-03-29 00:00:00",
    "adgroup_id": 1728545385226289
  },
  "metrics": {
    "cost_per_conversion": 0,
    "campaign_id": 1728545382536225,
    "campaign_name": "CampaignVadimTraffic",
    "clicks": 20,
    "dpa_target_audience_type": null,
    "mobile_app_id": "0",
    "promotion_type": "Website",
    "conversion_rate": 0,
    "cpm": 3.9,
    "cost_per_result": 0.3525,
    "cpc": 0.35,
    "real_time_cost_per_conversion": 0,
    "ctr": 1.11,
    "spend": 7.05,
    "result": 20,
    "real_time_result": 20,
    "impressions": 1806,
    "conversion": 0,
    "real_time_result_rate": 1.11,
    "real_time_conversion_rate": 0,
    "real_time_conversion": 0,
    "adgroup_name": "AdGroupVadim",
    "tt_app_name": "0",
    "placement": "Automatic Placement",
    "real_time_cost_per_result": 0.3525,
    "result_rate": 1.11,
    "tt_app_id": 0
  }
}
```

**CampaignsAudienceReportsByCountryDaily Stream - [AudienceReports](https://ads.tiktok.com/marketing_api/docs?id=1707957217727489)**
```
{
  "metrics": {
    "impressions": 5870,
    "campaign_name": "CampaignVadimTraffic",
    "cpm": 3.41,
    "clicks": 46,
    "spend": 20,
    "ctr": 0.78,
    "cpc": 0.43
  },
  "dimensions": {
    "stat_time_day": "2022-03-28 00:00:00",
    "campaign_id": 1728545382536225,
    "country_code": "US"
  }
}

```

## Performance considerations

The connector is restricted by [requests limitation](https://ads.tiktok.com/marketing_api/docs?rid=fgvgaumno25&id=1725359439428610). This connector should not run into TikTok Marketing API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                       |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------|
| 3.3.0   | 2023-07-05 | [27988](https://github.com/airbytehq/airbyte/pull/27988) | Add `category_exclusion_ids` field to `ad_groups` schema. |
| 3.2.1   | 2023-05-26 | [26569](https://github.com/airbytehq/airbyte/pull/26569) | Fixed syncs with `advertiser_id` provided in input configuration                              |
| 3.2.0   | 2023-05-25 | [26565](https://github.com/airbytehq/airbyte/pull/26565) | Change default value for `attribution window` to 3 days; add min/max validation               |
| 3.1.0   | 2023-05-12 | [26024](https://github.com/airbytehq/airbyte/pull/26024) | Updated the  `Ads` stream schema                                                              |
| 3.0.1   | 2023-04-07 | [24712](https://github.com/airbytehq/airbyte/pull/24712) | Added `attribution window` for *-reports streams                                              |
| 3.0.0   | 2023-03-29 | [24630](https://github.com/airbytehq/airbyte/pull/24630) | Migrate to v1.3 API                                                                           |
| 2.0.6   | 2023-03-30 | [22134](https://github.com/airbytehq/airbyte/pull/22134) | Add `country_code` and `platform` audience reports.                                           |
| 2.0.5   | 2023-03-29 | [22863](https://github.com/airbytehq/airbyte/pull/22863) | Specified date formatting in specification                                                    |
| 2.0.4   | 2023-02-23 | [22309](https://github.com/airbytehq/airbyte/pull/22309) | Add Advertiser ID to filter reports and streams                                               |
| 2.0.3   | 2023-02-15 | [23091](https://github.com/airbytehq/airbyte/pull/23091) | Add more clear log message for 504 error                                                      |
| 2.0.2   | 2023-02-02 | [22309](https://github.com/airbytehq/airbyte/pull/22309) | Chunk Advertiser IDs                                                                          |
| 2.0.1   | 2023-01-27 | [22044](https://github.com/airbytehq/airbyte/pull/22044) | Set `AvailabilityStrategy` for streams explicitly to `None`                                   |
| 2.0.0   | 2022-12-20 | [20415](https://github.com/airbytehq/airbyte/pull/20415) | Update schema types for `AudienceReports` and `BasicReports` streams.                         |
| 1.0.1   | 2022-12-16 | [20598](https://github.com/airbytehq/airbyte/pull/20598) | Remove Audience Reports with Hourly granularity due to deprecated dimension.                  |
| 1.0.0   | 2022-12-05 | [19758](https://github.com/airbytehq/airbyte/pull/19758) | Convert `mobile_app_id` from integer to string in AudienceReport streams.                     |
| 0.1.17  | 2022-10-04 | [17557](https://github.com/airbytehq/airbyte/pull/17557) | Retry error 50002                                                                             |
| 0.1.16  | 2022-09-28 | [17326](https://github.com/airbytehq/airbyte/pull/17326) | Migrate to per-stream state                                                                   |
| 0.1.15  | 2022-08-30 | [16137](https://github.com/airbytehq/airbyte/pull/16137) | Fixed bug with normalization caused by unsupported nested cursor field                        |
| 0.1.14  | 2022-06-29 | [13890](https://github.com/airbytehq/airbyte/pull/13890) | Removed granularity config option                                                             |
| 0.1.13  | 2022-06-28 | [13650](https://github.com/airbytehq/airbyte/pull/13650) | Added video metrics to report streams                                                         |
| 0.1.12  | 2022-05-24 | [13127](https://github.com/airbytehq/airbyte/pull/13127) | Fixed integration test                                                                        |
| 0.1.11  | 2022-04-27 | [12838](https://github.com/airbytehq/airbyte/pull/12838) | Added end date configuration for tiktok                                                       |
| 0.1.10  | 2022-05-07 | [12545](https://github.com/airbytehq/airbyte/pull/12545) | Removed odd production authenication method                                                   |
| 0.1.9   | 2022-04-30 | [12500](https://github.com/airbytehq/airbyte/pull/12500) | Improve input configuration copy                                                              |
| 0.1.8   | 2022-04-28 | [12435](https://github.com/airbytehq/airbyte/pull/12435) | updated spec descriptions                                                                     |
| 0.1.7   | 2022-04-27 | [12380](https://github.com/airbytehq/airbyte/pull/12380) | fixed spec descriptions and documentation                                                     |
| 0.1.6   | 2022-04-19 | [11378](https://github.com/airbytehq/airbyte/pull/11378) | updated logic for stream initializations, fixed errors in schemas, updated SAT and unit tests |
| 0.1.5   | 2022-02-17 | [10398](https://github.com/airbytehq/airbyte/pull/10398) | Add Audience reports                                                                          |
| 0.1.4   | 2021-12-30 | [7636](https://github.com/airbytehq/airbyte/pull/7636)   | Add OAuth support                                                                             |
| 0.1.3   | 2021-12-10 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                                      |
| 0.1.2   | 2021-12-02 | [8292](https://github.com/airbytehq/airbyte/pull/8292)   | Support reports                                                                               |
| 0.1.1   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                               |
| 0.1.0   | 2021-09-18 | [5887](https://github.com/airbytehq/airbyte/pull/5887)   | Release TikTok Marketing CDK Connector                                                        |
