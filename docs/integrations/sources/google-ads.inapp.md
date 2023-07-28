## Prerequisites

- A [Google Ads Account](https://support.google.com/google-ads/answer/6366720) [linked](https://support.google.com/google-ads/answer/7459601) to a Google Ads Manager account
<!-- env:oss -->
- (For Airbyte Open Source):
  - A Developer Token
  - The Client ID, Client Secret, and Refresh Token for your Google Ads account
<!-- /env:oss -->

## Setup guide

<!-- env:oss -->

### Step 1: (For Airbyte Open Source) Apply for a developer token

To set up the Google Ads source connector with Airbyte Open Source, you will need to obtain a developer token. This token allows you to access your data from the Google Ads API. Please note that Google is selective about which software and use cases are issued this token. The Airbyte team has worked with the Google Ads team to allowlist Airbyte and ensure you can get a developer token (see [issue 1981](https://github.com/airbytehq/airbyte/issues/1981) for more information on this topic).

1. To proceed with obtaining a developer token, you will first need to create a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/). Standard Google Ads accounts cannot generate a developer token.

2. To apply for the developer token, please follow [Google's instructions](https://developers.google.com/google-ads/api/docs/first-call/dev-token).

3. When you apply for the token, make sure to include the following:
    - Why you need the token (example: Want to run some internal analytics)
    - That you will be using the Airbyte Open Source project
    - That you have full access to the code base (because we're open source)
    - That you have full access to the server running the code (because you're self-hosting Airbyte)

:::note
You will _not_ be able to access your data via the Google Ads API until this token is approved. You cannot use a test developer token; it has to be at least a basic developer token. The approval process typically takes around 24 hours.
:::

### Step 2: (For Airbyte Open Source) Obtain your OAuth credentials

If you are using Airbyte Open Source, you will need to obtain the following OAuth credentials to authenticate your Google Ads account:

- Client ID
- Client Secret
- Refresh Token

Please refer to [Google's documentation](https://developers.google.com/identity/protocols/oauth2) for detailed instructions on how to obtain these credentials.

### Step 3: Set up the Google Ads connector in Airbyte

<!-- /env:oss -->
<!-- env:cloud -->

#### For Airbyte Cloud:

To set up Google Ads as a source in Airbyte Cloud:

1. [Log in to your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Ads** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Click **Sign in with Google** to authenticate your Google Ads account. In the pop-up, select the appropriate Google account and click **Continue** to proceed.
6. Enter a comma-separated list of the **Customer ID(s)** for your account. These IDs are 10-digit numbers that uniquely identify your account. To find your Customer ID, please follow [Google's instructions](https://support.google.com/google-ads/answer/1704344).
7. Enter a **Start Date** using the provided datepicker, or by programmatically entering the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
8. (Optional) You can use the **Custom GAQL Queries** field to enter a custom query using Google Ads Query Language. Click **Add** and enter your query, as well as the desired name of the table for this data in the destination. Multiple queries can be provided. For more information on formulating these queries, refer to our [guide below](#custom-query-understanding-google-ads-query-language).
9. (Required for Manager accounts) If the access to your account is through a Google Ads Manager account, you must enter the [**Login Customer ID for Managed Accounts**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Google Ads Manager account.
10. (Optional) Enter a **Conversion Window**. This is the number of days after an ad interaction during which a conversion is recorded in Google Ads. For more information on this topic, refer to the [Google Ads Help Center](https://support.google.com/google-ads/answer/3123169?hl=en).  This field defaults to 14 days.
11. (Optional) Enter an **End Date** in YYYY-MM-DD format. Any data added after this date will not be replicated. Leaving this field blank will replicate all data from the start date onward.
12. Click **Set up source** and wait for the tests to complete.
<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

To set up Google Ads as a source in Airbyte Open Source:

1. Log in to your Airbyte Open Source account.
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ New source**.
3. Find and select **Google Ads** from the list of available sources.
4. Enter a **Source name** of your choosing.
5. Enter the **Developer Token** you obtained from Google.
6. To authenticate your Google account, enter your Google application's **Client ID**, **Client Secret**, **Refresh Token**, and optionally, the **Access Token**.
7. Enter a comma-separated list of the **Customer ID(s)** for your account. These IDs are 10-digit numbers that uniquely identify your account. To find your Customer ID, please follow [Google's instructions](https://support.google.com/google-ads/answer/1704344).
8. Enter a **Start Date** using the provided datepicker, or by programmatically entering the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
9. (Optional) You can use the **Custom GAQL Queries** field to enter a custom query using Google Ads Query Language. Click **Add** and enter your query, as well as the desired name of the table for this data in the destination. Multiple queries can be provided. For more information on formulating these queries, refer to our [guide below](#custom-query-understanding-google-ads-query-language).
10. (Optional) If the access to your account is through a [Google Ads Manager account](https://ads.google.com/home/tools/manager-accounts/), enter the [**Login Customer ID for Managed Accounts**](https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid) of the Google Ads Manager account.
11. (Optional) Enter a **Conversion Window**. This is the number of days after an ad interaction during which a conversion is recorded in Google Ads. For more information on this topic, refer to the [Google Ads Help Center](https://support.google.com/google-ads/answer/3123169?hl=en). This field defaults to 14 days.
12. (Optional) Enter an **End Date** in YYYY-MM-DD format. Any data added after this date will not be replicated. Leaving this field blank will replicate all data from the start date onward.
13. Click **Set up source** and wait for the tests to complete.

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

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Ads](https://docs.airbyte.com/integrations/sources/google-ads/).
