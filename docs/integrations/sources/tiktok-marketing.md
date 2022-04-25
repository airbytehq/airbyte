# TikTok Marketing

## Overview

The [TikTok For Business Marketing API](https://ads.tiktok.com/marketing_api/homepage?rid=uvtbok1h19) allows you to directly interact with the TikTok Ads Manager platform for automated ad management and analysis. 

The TikTok Marketing source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Streams information

| Stream                            | Environment  | Granularities     | Key         | Incremental    | Schema                                                                                        |
|:----------------------------------|--------------|-------------------|-------------|:---------------|-----------------------------------------------------------------------------------------------|
| Advertisers                       | Prod,Sandbox | LIFETIME,DAY,HOUR | id          | No             | [Link](https://business-api.tiktok.com/marketing_api/docs?id=1708503202263042)                |
| AdGroups                          | Prod,Sandbox | LIFETIME,DAY,HOUR | adgroup_id  | Yes (DAY,HOUR) | [Link](https://business-api.tiktok.com/marketing_api/docs?id=1708503489590273)                |
| Ads                               | Prod,Sandbox | LIFETIME,DAY,HOUR | ad_id       | Yes (DAY,HOUR) | [Link](https://business-api.tiktok.com/marketing_api/docs?id=1708572923161602)                |
| Campaigns                         | Prod,Sandbox | LIFETIME,DAY,HOUR | campaign_id | Yes (DAY,HOUR) | [Link](https://business-api.tiktok.com/marketing_api/docs?id=1708582970809346)                |
| AdsReports                        | Prod,Sandbox | LIFETIME,DAY,HOUR | None        | Yes (DAY,HOUR) | [BasicReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957200780290)    |
| AdvertisersReports                | Prod         | LIFETIME,DAY,HOUR | None        | Yes (DAY,HOUR) | [BasicReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957200780290)    |
| AdGroupsReports                   | Prod,Sandbox | LIFETIME,DAY,HOUR | None        | Yes (DAY,HOUR) | [BasicReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957200780290)    |
| CampaignsReports                  | Prod,Sandbox | LIFETIME,DAY,HOUR | None        | Yes (DAY,HOUR) | [BasicReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957200780290)    |
| AdvertisersAudienceReports        | Prod         | LIFETIME,DAY,HOUR | None        | Yes (DAY,HOUR) | [AudienceReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957217727489) |
| AdGroupAudienceReports            | Prod,Sandbox | DAY,HOUR          | None        | Yes (DAY,HOUR) | [AudienceReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957217727489) |
| AdsAudienceReports                | Prod,Sandbox | DAY,HOUR          | None        | Yes (DAY,HOUR) | [AudienceReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957217727489) |
| CampaignsAudienceReportsByCountry | Prod,Sandbox | DAY,HOUR          | None        | Yes (DAY,HOUR) | [AudienceReportsLink](https://business-api.tiktok.com/marketing_api/docs?id=1707957217727489) |

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is restricted by [requests limitation](https://ads.tiktok.com/marketing_api/docs?rid=fgvgaumno25&id=1701890997610497). This connector should not run into TikTok Marketing API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Access Token - This token will not expire. 
* Production Environment
  * App ID
  * Secret
* SandBox Environment
  * Advertiser ID - It is generated for sandbox in one copy

### Setup guide

Please read [How to get your AppID, Secret and Access Token](https://ads.tiktok.com/marketing_api/docs?rid=fgvgaumno25&id=1701890909484033) or [How to create a SandBox Environment](https://ads.tiktok.com/marketing_api/docs?rid=fgvgaumno25&id=1701890920013825)

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                                       |
|:--------|:-----------|:---------------------------------------------------------|:----------------------------------------------------------------------------------------------|
| 0.1.6   | 2022-04-19 | [11378](https://github.com/airbytehq/airbyte/pull/11378) | updated logic for stream initializations, fixed errors in schemas, updated SAT and unit tests |
| 0.1.5   | 2022-02-17 | [10398](https://github.com/airbytehq/airbyte/pull/10398) | Add Audience reports                                                                          |
| 0.1.4   | 2021-12-30 | [7636](https://github.com/airbytehq/airbyte/pull/7636)   | Add OAuth support                                                                             |
| 0.1.3   | 2021-12-10 | [8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                                      |
| 0.1.2   | 2021-12-02 | [8292](https://github.com/airbytehq/airbyte/pull/8292)   | Support reports                                                                               |
| 0.1.1   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                                                               |
| 0.1.0   | 2021-09-18 | [5887](https://github.com/airbytehq/airbyte/pull/5887)   | Release TikTok Marketing CDK Connector                                                        |
