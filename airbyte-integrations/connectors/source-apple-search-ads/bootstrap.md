## Base streams

Apple Search Ads is a REST based API. Connector is implemented with the [Airbyte Low-Code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview/)

Connector has base streams including attributes about entities in the API (e.g: what campaigns, which adgroups, etc…), and all of them support full refresh only:

- [Campaigns](https://developer.apple.com/documentation/apple_search_ads/get_all_campaigns)
- [AdGroups](https://developer.apple.com/documentation/apple_search_ads/get_all_ad_groups)
- [Keywords](https://developer.apple.com/documentation/apple_search_ads/get_all_targeting_keywords_in_an_ad_group)

## Report streams

Connector also has report streams including statistics about entities (e.g: how many spending on a campaign, how many clicks on a keyword, etc...) which support incremental sync.

- [Campaign-Level Report](https://developer.apple.com/documentation/apple_search_ads/get_campaign-level_reports)
- [Ad Group-Level Report](https://developer.apple.com/documentation/apple_search_ads/get__ad_group-level_reports)
- [Keyword-Level Report](https://developer.apple.com/documentation/apple_search_ads/get_keyword-level_reports)

Connector uses `start_date` config for initial reports sync and current date as an end date if this one is not explicitly set.

At the moment, report streams are only set to the `DAILY` granularity (e.g: `campaigns_report_daily`, `adgroups_report_daily`, `keywords_report_daily`).

See [this](https://docs.airbyte.io/integrations/sources/apple-search-ads) link for the nuances about the connector.
