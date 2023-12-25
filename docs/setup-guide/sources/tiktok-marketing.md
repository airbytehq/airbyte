# TikTok Marketing

This page contains the setup guide and reference information for TikTok Marketing.

## Prerequisites

* A Tiktok Ads Business account with permission to access data from accounts you want to sync

## Setup guide

### Step 1: Set up TikTok

1. Create a **TikTok For Business account** [here](https://ads.tiktok.com/i18n/signup/).

2. Follow [this guide](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1738855176671234) to **Register as a TikTok developer**.

3. Follow [this guide](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1738855242728450) to **Create a TikTok developer app**.

  > Follow [this guide](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1738855331457026) to **Create a TikTok Sandbox Ad Account**.

### Step 2: Obtain the Access token

1. Inside the app you created in Step 1, you will find the **Access token**, **Secret**, and **App ID**. Copy them and use them to set up the source in Daspire.

### Step 3: Set up TikTok Marketing in Daspire

1. Select **TikTok Marketing** from the Source list.

2. Enter a **Source Name**.

3. To authenticate your account, select **Production Access Token** or **Sandbox Access Token** and enter the Access Token you generated in Step 2.

4. For **Start Date**, enter a UTC date and time in the format `YYYY-MM-DDTHH:mm:ssZ`. The data added on and after this date will be replicated.

5. Click **Save & Test**.

## Output schema

This Source is capable of syncing the following core Streams:

| Stream | Environment | Key | Incremental |
| --- | --- | --- | --- |
| Advertisers | Production, Sandbox | advertiser_id | No |
| AdGroups | Production, Sandbox | adgroup_id | Yes |
| Ads | Production, Sandbox | ad_id | Yes |
| AdsReportsHourly | Production, Sandbox | ad_id, stat_time_hour | Yes |
| AdsReportsDaily | Production, Sandbox | ad_id, stat_time_day | Yes |
| AdsReportsLifetime | Production, Sandbox | ad_id | No |
| AdvertisersReportsHourly | Production | advertiser_id, stat_time_hour | Yes |
| AdvertisersReportsDaily | Production | advertiser_id, stat_time_day | Yes |
| AdvertisersReportsLifetime | Production | advertiser_id | No |
| AdGroupsReportsHourly | Production, Sandbox | adgroup_id, stat_time_hour | Yes |
| AdGroupsReportsDaily | Production, Sandbox | adgroup_id, stat_time_day | Yes |
| AdGroupsReportsLifetime | Production, Sandbox | adgroup_id, stat_time_day | Yes |
| AdGroupsReportsDaily | Production, Sandbox | adgroup_id | No |
| Audiences | Production, Sandbox | audience_id | No |
| Campaigns | Production, Sandbox | campaign_id | No |
| CampaignsReportsHourly | Production, Sandbox | campaign_id, stat_time_hour | Yes |
| CampaignsReportsDaily | Production, Sandbox | campaign_id, stat_time_day | Yes |
| CampaignsReportsLifetime | Production, Sandbox | campaign_id | No |
| CreativeAssetsImages | Production, Sandbox | image_id | Yes |
| CreativeAssetsMusic | Production, Sandbox | music_id | Yes |
| CreativeAssetsPortfolios | Production, Sandbox | creative_portfolio_id | No |
| CreativeAssetsVideos | Production, Sandbox | video_id | Yes |
| AdvertiserIds | Production | advertiser_id | Yes |
| AdvertisersAudienceReportsDaily | Production | advertiser_id, stat_time_day, gender, age | Yes |
| AdvertisersAudienceReportsByCountryDaily | Production | advertiser_id, stat_time_day, country_code | Yes |
| AdvertisersAudienceReportsByPlatformDaily | Production | advertiser_id, stat_time_day, platform | Yes |
| AdvertisersAudienceReportsLifetime | Production | advertiser_id, gender, age | No |
| AdGroupAudienceReportsDaily | Production, Sandbox | adgroup_id, stat_time_day, gender, age | Yes |
| AdGroupAudienceReportsByCountryDaily | Production, Sandbox | adgroup_id, stat_time_day, country_code | Yes |
| AdGroupAudienceReportsByPlatformDaily | Production, Sandbox | adgroup_id, stat_time_day, platform | Yes |
| AdsAudienceReportsDaily | Production, Sandbox | ad_id, stat_time_day, gender, age | Yes |
| AdsAudienceReportsByCountryDaily | Production, Sandbox | ad_id, stat_time_day, country_code | Yes |
| AdsAudienceReportsByPlatformDaily | Production, Sandbox | ad_id, stat_time_day, platform | Yes |
| AdsAudienceReportsByProvinceDaily | Production, Sandbox | ad_id, stat_time_day, province_id | Yes |
| CampaignsAudienceReportsDaily | Production, Sandbox | campaign_id, stat_time_day, gender, age | Yes |
| CampaignsAudienceReportsByCountryDaily | Production, Sandbox | campaign_id, stat_time_day, country_code | Yes |
| CampaignsAudienceReportsByPlatformDaily | Production, Sandbox | campaign_id, stat_time_day, platform | Yes |

### Data latency

TikTok Reporting API has some [Data Latency](https://ads.tiktok.com/marketing_api/docs?id=1738864894606337), usually of about 11 hours. It is recommended to use higher values of attribution window (used in Incremental Syncs), at least 3 days, to ensure that the integration updates metrics in already presented records.

### Report aggregation

Reports synced by this integration can use either hourly, daily, or lifetime granularities for aggregating performance data. For example, if you select the daily-aggregation flavor of a report, the report will contain a row for each day for the duration of the report. Each row will indicate the number of impressions recorded on that day.

## Performance considerations & troubleshooting

1. The integration is restricted by [TikTok Marketing API requests limitation](https://business-api.tiktok.com/portal/docs?rid=fgvgaumno25&id=1740029171730433). This integration should not run into the limitations under normal usage.

2. Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
