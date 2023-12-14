
## Core streams

Bing Ads is a SOAP based API. Connector is implemented with [SDK](https://github.com/BingAds/BingAds-Python-SDK) library

Connector has such core streams, and all of them support full refresh only:
* [Account](https://docs.microsoft.com/en-us/advertising/customer-management-service/advertiseraccount?view=bingads-13)
* [Campaign](https://docs.microsoft.com/en-us/advertising/campaign-management-service/campaign?view=bingads-13)
* [AdGroup](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadgroupsbycampaignid?view=bingads-13)
* [Ad](https://docs.microsoft.com/en-us/advertising/campaign-management-service/getadsbyadgroupid?view=bingads-13)


## Report streams

Connector also has report streams, which support incremental sync.

* [AccountPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/accountperformancereportrequest?view=bingads-13)
* [AdPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/adperformancereportrequest?view=bingads-13)
* [AdGroupPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/adgroupperformancereportrequest?view=bingads-13)
* [CampaignPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/campaignperformancereportrequest?view=bingads-13)
* [BudgetSummaryReport](https://docs.microsoft.com/en-us/advertising/reporting-service/budgetsummaryreportrequest?view=bingads-13)
* [KeywordPerformanceReport](https://docs.microsoft.com/en-us/advertising/reporting-service/keywordperformancereportrequest?view=bingads-13)

To be able to pull report data you need to generate 2 separate requests.

* [First](https://docs.microsoft.com/en-us/advertising/reporting-service/submitgeneratereport?view=bingads-13) - to request appropriate report

* [Second](https://docs.microsoft.com/en-us/advertising/reporting-service/pollgeneratereport?view=bingads-13) - to poll acatual data. Report download timeout is 5 min

Initially all fields in report streams have string values, connector uses `reports.REPORT_FIELD_TYPES` collection to transform values to numerical fields if possible

Connector uses `reports_start_date` config for initial reports sync and current date as an end data.

Connector has `hourly_reports`, `daily_reports`, `weekly_reports`, `monthly_reports` report streams. For example `account_performance_report_daily`, `ad_group_performance_report_weekly`. All these reports streams will be generated on execute.

If `lookback_window` is set to a non-null value, initial reports sync will start at `reports_start_date - lookback_window`. Following reports sync will start at `cursor_value - lookback_window`. 

## Request caching

Based on [library](https://vcrpy.readthedocs.io/en/latest/)

Connector uses caching for these streams:

* Account
* Campaign
* AdGroup

See [this](https://docs.airbyte.io/integrations/sources/bing-ads) link for the nuances about the connector.
