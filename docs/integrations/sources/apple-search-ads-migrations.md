# Apple Ads (Apple Search Ads) Migration Guide

## Upgrading to 1.0.0

Version 1.0.0 of the Apple Ads connector has shifted to use a global cursor state for both [adgroups_report_daily](https://developer.apple.com/documentation/apple_search_ads/get__ad_group-level_reports) and [keywords_report_daily](https://developer.apple.com/documentation/apple_search_ads/get_keyword-level_reports)  
When upgrading to this version, the connector state must be manually changed to allow continued operation. Be sure
to replace `YYYY-MM-DD` with the date you last synced these streams

```json
[
   ...
   {
      "streamDescriptor":{
         "name":"keywords_report_daily"
      },
      "streamState":{
         "state":{
            "date":"YYYY-MM-DD"
         },
         "parent_state":{
            
         },
         "use_global_cursor":true
      }
   },
   {
      "streamDescriptor":{
         "name":"adgroups_report_daily"
      },
      "streamState":{
         "state":{
            "date":"YYYY-MM-DD"
         },
         "parent_state":{
            
         },
         "use_global_cursor":true
      }
   }
]
```
