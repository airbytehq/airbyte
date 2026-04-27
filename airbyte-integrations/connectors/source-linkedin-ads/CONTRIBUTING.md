# Contributing to source-linkedin-ads

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

The LinkedIn Marketing API supports date-based filtering on analytics and campaign/creative endpoints, which the connector already uses for 17 incremental streams. The single remaining FR parent stream (`accounts`) is a config-style endpoint listing ad accounts, which does not support date-based filtering on its list endpoint.

| Stream | Volume Tier | Relationship | Cursor Field | API Incremental Support | Current Status | Notes |
|---|---|---|---|---|---|---|
| accounts | small | top-level parent | none | none | deferred_no_api_support | Lists ad accounts; config-style, typically <10 accounts per org |
| account_users | medium | child | lastModified | lastModified | incremental |  |
| ad_campaign_analytics | medium | child | end_date | end_date | incremental |  |
| ad_creative_analytics | medium | child | end_date | end_date | incremental |  |
| ad_impression_device_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_company_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_company_size_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_country_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_industry_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_job_function_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_job_title_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_region_analytics | medium | child | end_date | end_date | incremental |  |
| ad_member_seniority_analytics | medium | child | end_date | end_date | incremental |  |
| campaign_groups | medium | child | lastModified | lastModified | incremental |  |
| campaigns | medium | child | lastModified | lastModified | incremental |  |
| conversions | medium | child | lastModified | lastModified | incremental |  |
| creatives | medium | child | lastModifiedAt | lastModifiedAt | incremental |  |
| custom_analytics_report | medium | child | end_date | end_date | incremental |  |
| lead_form_responses | medium | child | none | none | deferred_child |  |
| lead_forms | medium | child | none | none | deferred_child |  |

### Deferred streams

- **No API date filter (1 streams):** `accounts` — these endpoints do not expose date-based filtering. A future agent should verify via live API probing whether undocumented filter parameters are accepted.
- **Child streams (2 streams):** `lead_form_responses`, `lead_forms` — partitioned via `SubstreamPartitionRouter`. A follow-up session should evaluate incremental support.
