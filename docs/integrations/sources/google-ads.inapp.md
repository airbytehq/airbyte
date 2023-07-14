## Prerequisites

- A [Google Ads Account](https://support.google.com/google-ads/answer/6366720) [linked](https://support.google.com/google-ads/answer/7459601) to a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/)

## Setup guide
1. Enter a **Name** for your source.
2. Click **Sign in with Google** to authenticate your Google Ads account.
3. Enter a comma-separated list of the [Customer ID(s)](https://support.google.com/google-ads/answer/1704344) for your account.
4. Enter the **Start Date** in YYYY-MM-DD format. The data added on and after this date will be replicated. If this field is blank, Airbyte will replicate all data.
5. (Optional) Enter a custom [GAQL](#custom-query-understanding-google-ads-query-language) query.
6. (Optional) If the access to your account is through a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/), enter the [**Login Customer ID for Managed Accounts**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Google Ads Manager account.
7. (Optional) Enter a [**Conversion Window**](https://support.google.com/google-ads/answer/3123169?hl=en).
8. (Optional) Enter the **End Date** in YYYY-MM-DD format. The data added after this date will not be replicated.
9. Click **Set up source**.

## Custom Query: Understanding Google Ads Query Language
Additional streams for Google Ads can be dynamically created using custom queries. 

The Google Ads Query Language queries the Google Ads API. Review the [Google Ads Query Language](https://developers.google.com/google-ads/api/docs/query/overview) and the [query builder](https://developers.google.com/google-ads/api/fields/v13/query_validator) to validate your query. You can then add these as custom queries when configuring the Google Ads source.

Example GAQL Custom Query:
```
SELECT 
    campaign.name, 
    metrics.conversions, 
    metrics.conversions_by_conversion_date 
FROM ad_group
```
Note the segments.date is automatically added to the output, and does not need to be specified in the custom query. All custom reports will by synced by day.

Each custom query in the input configuration must work for all the customer account IDs. Otherwise, the customer ID will be skipped for every query that fails the validation test. For example, if your query contains metrics fields in the select clause, it will not be executed against manager accounts.

Follow Google's guidance on [Selectability between segments and metrics](https://developers.google.com/google-ads/api/docs/reporting/segmentation#selectability_between_segments_and_metrics) when editing custom queries or default stream schemas (which will also be turned into GAQL queries by the connector). Fields like `segments.keyword.info.text`, `segments.keyword.info.match_type`, `segments.keyword.ad_group_criterion` in the `SELECT` clause tell the query to only get the rows of data that have keywords and remove any row that is not associated with a keyword. This is often unobvious and undesired behavior and can lead to missing data records. If you need this field in the stream, add a new stream instead of editing the existing ones.

:::info
For an existing Google Ads source, when you are updating or removing Custom GAQL Queries, you should also subsequently refresh your source schema to pull in any changes.
:::

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Ads](https://docs.airbyte.com/integrations/sources/google-ads/).
