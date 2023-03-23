The Business Marketing API is [a REST based API](https://business-api.tiktok.com/marketing_api/docs?rid=88iodtuzdt7&id=1701890905779201). Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).
This service also provides a [sandbox](https://business-api.tiktok.com/marketing_api/docs?rid=88iodtuzdt7&id=1701890920013825) environment for testing with some limitations.

## Core Advertiser stream
The basic entity is 'advertiser'. All other streams use this required parameter for data loading. This works slightly differently between sandbox and production environments. For production, every developer application can have multiple advertisers. [This endpoint](https://business-api.tiktok.com/marketing_api/docs?id=1708503202263042) gets a list of advertiser accounts that authorized an app, providing us functionality to obtain the associated advertisers. However, this endpoint is inaccessible for sandbox because a sandbox can have only one advertiser object and its ID is known in advance.

## Other streams
* [Campaigns](https://business-api.tiktok.com/marketing_api/docs?id=1708582970809346) \(Incremental\)
* [Ad Groups](https://business-api.tiktok.com/marketing_api/docs?id=1708503489590273)\(Incremental\)
* [Ads](https://business-api.tiktok.com/marketing_api/docs?id=1708572923161602)\(Incremental\)

Dependent streams have required parameter advertiser_id.
As cursor field this connector uses "modify_time" values. But endpoints don't provide any mechanism for correct data filtering and sorting thus for incremental sync this connector tries to load all data and to validate a cursor field value on own side.



`stream` method has granularity condition depend on that report streams supports by different connector version:
- For all version:
  basic streams list: 
     * ad_groups
     * ads
     * campaigns
     * advertisers
- for < 0.1.13 - expose report streams initialized with 'report_granularity' argument, like:
  Example: 
  - AdsReports(report_granularity='DAILY')
  - AdsReports(report_granularity='LIFETIME')
  streams list:
    * advertisers_reports
    * advertisers_audience_reports
    * campaigns_audience_reports_by_country
    * ad_group_audience_reports
    * ads_audience_reports
    * ad_groups_reports
    * ads_reports
    * campaigns_reports

- for >= 0.1.13 - expose report streams in format: <report_type>_<granularity>, like:
  Example: 
  - AdsReportsDaily(Daily, AdsReports)
  - AdsReportsLifetime(Lifetime, AdsReports)
  streams:
    * campaigns_audience_reports_by_country_daily
    * campaigns_reports_daily 
    * advertisers_audience_reports_daily
    * advertisers_reports_daily
    * ad_group_audience_reports_daily
    * ads_reports_lifetime
    * advertiser_ids
    * campaigns_reports_lifetime
    * advertisers_audience_reports_lifetime
    * ad_groups_reports_lifetime
    * ad_groups_reports_daily
    * advertisers_reports_lifetime
    * ads_reports_daily
    * ads_audience_reports_daily
    * ads_reports_hourly
    * ad_groups_reports_hourly
    * advertisers_reports_hourly
    * campaigns_reports_hourly
