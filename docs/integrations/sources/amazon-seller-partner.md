# Amazon Seller Partner

This page guides you through the process of setting up the Amazon Seller Partner source connector.

:::caution

Authenticating this Alpha connector is currently blocked. This is a known issue being tracked here: https://github.com/airbytehq/airbyte/issues/14734

:::

## Prerequisites

- app_id
- lwa_app_id
- lwa_client_secret
- refresh_token
- aws_access_key
- aws_secret_key
- role_arn
- aws_environment
- region
- replication_start_date

## Step 1: Set up Amazon Seller Partner

[Register](https://developer-docs.amazon.com/sp-api/docs/registering-your-application) Amazon Seller Partner application.
[Create](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) IAM user.

## Step 2: Set up the source connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) account. 
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
3. On the source setup page, select **Amazon Seller Partner** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your account`.
5. Log in and Authorize to the Amazon Seller Partner account.
6. Paste all other data to required fields using your IAM user.
7. Click `Set up source`.

**For Airbyte Open Source:**

1. Using developer application from Step 1, [generate](https://developer-docs.amazon.com/sp-api/docs/self-authorization) refresh token. 
2. Go to local Airbyte page.
3. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
4. On the Set up the source page, enter the name for the Amazon Seller Partner connector and select **Amazon Seller Partner** from the Source type dropdown. 
5. Paste all data to required fields using your IAM user and developer account.
6. Click `Set up source`.

## Supported sync modes

The Amazon Seller Partner source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-mode):
 - Full Refresh
 - Incremental

## Performance considerations

Information about rate limits you may find [here](https://developer-docs.amazon.com/sp-api/docs/usage-plans-and-rate-limits-in-the-sp-api).

## Supported streams

This source is capable of syncing the following tables and their data:
- [FBA Inventory Reports](https://sellercentral.amazon.com/gp/help/200740930)
- [FBA Orders Reports](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110)
- [FBA Shipments Reports](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989100)
- [FBA Replacements Reports](https://sellercentral.amazon.com/help/hub/reference/200453300)
- [FBA Storage Fees Report](https://sellercentral.amazon.com/help/hub/reference/G202086720)
- [Restock Inventory Reports](https://sellercentral.amazon.com/help/hub/reference/202105670)
- [Flat File Open Listings Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Flat File Orders Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Flat File Orders Reports By Last Update](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference) \(incremental\)
- [Amazon-Fulfilled Shipments Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Merchant Listings Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Vendor Direct Fulfillment Shipping](https://developer-docs.amazon.com/sp-api/docs/vendor-direct-fulfillment-shipping-api-v1-reference)
- [Vendor Inventory Health Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Orders](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference) \(incremental\)
- [Seller Feedback Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference) \(incremental\)
- [Brand Analytics Alternate Purchase Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
- [Brand Analytics Item Comparison Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
- [Brand Analytics Market Basket Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
- [Brand Analytics Repeat Purchase Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
- [Brand Analytics Search Terms Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
- [Browse tree report](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#browse-tree-report)
- [Financial Event Groups](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialeventgroups)
- [Financial Events](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialevents)

## Data type mapping

| Integration Type         | Airbyte Type |
| :----------------------- | :----------- |
| `string`                 | `string`     |
| `int`, `float`, `number` | `number`     |
| `date`                   | `date`       |
| `datetime`               | `datetime`   |
| `array`                  | `array`      |
| `object`                 | `object`     |


## Changelog

| Version  | Date       | Pull Request                                               | Subject                                                                |
|:---------|:-----------|:-----------------------------------------------------------|:-----------------------------------------------------------------------|
| `0.2.25` | 2022-07-27 | [\#15063](https://github.com/airbytehq/airbyte/pull/15063) | Add Restock Inventory Report                                            |
| `0.2.24` | 2022-07-12 | [\#14625](https://github.com/airbytehq/airbyte/pull/14625) | Add FBA Storage Fees Report                                            |
| `0.2.23` | 2022-06-08 | [\#13604](https://github.com/airbytehq/airbyte/pull/13604) | Add new streams: Fullfiments returns and Settlement reports            |
| `0.2.22` | 2022-06-15 | [\#13633](https://github.com/airbytehq/airbyte/pull/13633) | Fix - handle start date for financial stream                           |
| `0.2.21` | 2022-06-01 | [\#13364](https://github.com/airbytehq/airbyte/pull/13364) | Add financial streams                                                  |
| `0.2.20` | 2022-05-30 | [\#13059](https://github.com/airbytehq/airbyte/pull/13059) | Add replication end date to config                                     |
| `0.2.19` | 2022-05-24 | [\#13119](https://github.com/airbytehq/airbyte/pull/13119) | Add OAuth2.0 support                                                   |
| `0.2.18` | 2022-05-06 | [\#12663](https://github.com/airbytehq/airbyte/pull/12663) | Add GET_XML_BROWSE_TREE_DATA report                                    |
| `0.2.17` | 2022-05-19 | [\#12946](https://github.com/airbytehq/airbyte/pull/12946) | Add throttling exception managing in Orders streams                    |
| `0.2.16` | 2022-05-04 | [\#12523](https://github.com/airbytehq/airbyte/pull/12523) | allow to use IAM user arn or IAM role arn                              |
| `0.2.15` | 2022-01-25 | [\#9789](https://github.com/airbytehq/airbyte/pull/9789)   | Add stream FbaReplacementsReports                                      |
| `0.2.14` | 2022-01-19 | [\#9621](https://github.com/airbytehq/airbyte/pull/9621)   | Add GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL report        |
| `0.2.13` | 2022-01-18 | [\#9581](https://github.com/airbytehq/airbyte/pull/9581)   | Change createdSince parameter to dataStartTime                         |
| `0.2.12` | 2022-01-05 | [\#9312](https://github.com/airbytehq/airbyte/pull/9312)   | Add all remaining brand analytics report streams                       |
| `0.2.11` | 2022-01-05 | [\#9115](https://github.com/airbytehq/airbyte/pull/9115)   | Fix reading only 100 orders                                            |
| `0.2.10` | 2021-12-31 | [\#9236](https://github.com/airbytehq/airbyte/pull/9236)   | Fix NoAuth deprecation warning                                         |
| `0.2.9`  | 2021-12-30 | [\#9212](https://github.com/airbytehq/airbyte/pull/9212)   | Normalize GET_SELLER_FEEDBACK_DATA header field names                  |
| `0.2.8`  | 2021-12-22 | [\#8810](https://github.com/airbytehq/airbyte/pull/8810)   | Fix GET_SELLER_FEEDBACK_DATA Date cursor field format                  |
| `0.2.7`  | 2021-12-21 | [\#9002](https://github.com/airbytehq/airbyte/pull/9002)   | Extract REPORTS_MAX_WAIT_SECONDS to configurable parameter             |
| `0.2.6`  | 2021-12-10 | [\#8179](https://github.com/airbytehq/airbyte/pull/8179)   | Add GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT report                     |
| `0.2.5`  | 2021-12-06 | [\#8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                               |
| `0.2.4`  | 2021-11-08 | [\#8021](https://github.com/airbytehq/airbyte/pull/8021)   | Added GET_SELLER_FEEDBACK_DATA report with incremental sync capability |
| `0.2.3`  | 2021-11-08 | [\#7828](https://github.com/airbytehq/airbyte/pull/7828)   | Remove datetime format from all streams                                |
| `0.2.2`  | 2021-11-08 | [\#7752](https://github.com/airbytehq/airbyte/pull/7752)   | Change `check_connection` function to use stream Orders                |
| `0.2.1`  | 2021-09-17 | [\#5248](https://github.com/airbytehq/airbyte/pull/5248)   | `Added extra stream support. Updated reports streams logics`           |
| `0.2.0`  | 2021-08-06 | [\#4863](https://github.com/airbytehq/airbyte/pull/4863)   | `Rebuild source with airbyte-cdk`                                      |
| `0.1.3`  | 2021-06-23 | [\#4288](https://github.com/airbytehq/airbyte/pull/4288)   | `Bugfix failing connection check`                                      |
| `0.1.2`  | 2021-06-15 | [\#4108](https://github.com/airbytehq/airbyte/pull/4108)   | `Fixed: Sync fails with timeout when create report is CANCELLED`       |
