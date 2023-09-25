## Prerequisites

- A [Google Ads Account](https://support.google.com/google-ads/answer/6366720) [linked](https://support.google.com/google-ads/answer/7459601) to a Google Ads Manager account
<!-- env:oss -->
- (For Airbyte Open Source):
  - A Developer Token
  - OAuth credentials to authenticate your Google account
<!-- /env:oss -->

## Setup guide

<!-- env:oss -->

To set up the Google Ads source connector with Airbyte Open Source, you will first need to obtain a developer token, as well as credentials for OAuth authentication. For more information on the steps involved, please refer to our [full documentation](https://docs.airbyte.com/integrations/sources/google-ads#setup-guide).

<!-- /env:oss -->
<!-- env:cloud -->

### For Airbyte Cloud:

1. Enter a **Source name** of your choosing.
2. Click **Sign in with Google** to authenticate your Google Ads account. In the pop-up, select the appropriate Google account and click **Continue** to proceed.
3. Enter a comma-separated list of the **Customer ID(s)** for your account. These IDs are 10-digit numbers that uniquely identify your account. To find your Customer ID, please follow [Google's instructions](https://support.google.com/google-ads/answer/1704344).
4. Enter a **Start Date** using the provided datepicker, or by programmatically entering the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
5. (Optional) You can use the **Custom GAQL Queries** field to enter a custom query using Google Ads Query Language. Click **Add** and enter your query, as well as the desired name of the table for this data in the destination. Multiple queries can be provided. For more information on formulating these queries, refer to our [guide below](#custom-query-understanding-google-ads-query-language).
6. (Required for Manager accounts) If accessing your account through a Google Ads Manager account, you must enter the [**Customer ID**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Manager account.
7. (Optional) Enter a **Conversion Window**. This is the number of days after an ad interaction during which a conversion is recorded in Google Ads. For more information on this topic, refer to the [Google Ads Help Center](https://support.google.com/google-ads/answer/3123169?hl=en).  This field defaults to 14 days.
8. (Optional) Enter an **End Date** in YYYY-MM-DD format. Any data added after this date will not be replicated. Leaving this field blank will replicate all data from the start date onward.
9. Click **Set up source** and wait for the tests to complete.
<!-- /env:cloud -->

<!-- env:oss -->

### For Airbyte Open Source:

1. Enter a **Source name** of your choosing.
2. Enter the **Developer Token** you obtained from Google.
3. To authenticate your Google account, enter your Google application's **Client ID**, **Client Secret**, **Refresh Token**, and optionally, the **Access Token**.
4. Enter a comma-separated list of the **Customer ID(s)** for your account. These IDs are 10-digit numbers that uniquely identify your account. To find your Customer ID, please follow [Google's instructions](https://support.google.com/google-ads/answer/1704344).
5. Enter a **Start Date** using the provided datepicker, or by programmatically entering the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
6. (Optional) You can use the **Custom GAQL Queries** field to enter a custom query using Google Ads Query Language. Click **Add** and enter your query, as well as the desired name of the table for this data in the destination. Multiple queries can be provided. For more information on formulating these queries, refer to our [guide below](#custom-query-understanding-google-ads-query-language).
7. (Required for Manager accounts) If accessing your account through a Google Ads Manager account, you must enter the [**Customer ID**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Manager account.
8. (Optional) Enter a **Conversion Window**. This is the number of days after an ad interaction during which a conversion is recorded in Google Ads. For more information on this topic, refer to the [Google Ads Help Center](https://support.google.com/google-ads/answer/3123169?hl=en). This field defaults to 14 days.
9. (Optional) Enter an **End Date** in YYYY-MM-DD format. Any data added after this date will not be replicated. Leaving this field blank will replicate all data from the start date onward.
10. Click **Set up source** and wait for the tests to complete.

<!-- /env:oss -->

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

For detailed information on supported sync modes, supported streams, performance considerations, refer to the [full documentation for Google Ads](https://docs.airbyte.com/integrations/sources/google-ads/).
