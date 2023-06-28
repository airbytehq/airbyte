# Amazon Seller Partner

This page guides you through the process of setting up the Amazon Seller Partner source connector.

## Prerequisites

- AWS Environment
- AWS Region
- AWS Access Key
- AWS Secret Key
- Role ARN
- LWA Client ID (LWA App ID)**
- LWA Client Secret**
- Refresh token**
- Replication Start Date

**not required for Airbyte Cloud

## Step 1: Set up Amazon Seller Partner

1. [Register](https://developer-docs.amazon.com/sp-api/docs/registering-your-application) Amazon Seller Partner application.
    - The application must be published as Amazon does not allow external parties such as Airbyte to access draft applications.
2. [Create](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) IAM user.

## Step 2: Set up the source connector in Airbyte

**For Airbyte Cloud:**

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account. 
2. In the left navigation bar, click **Sources**. In the top-right corner, click **+ new source**. 
3. On the source setup page, select **Amazon Seller Partner** from the Source type dropdown and enter a name for this connector.
4. Click `Authenticate your account`.
5. Log in and Authorize to your Amazon Seller Partner account.
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
- [Manage FBA Inventory Reports](https://sellercentral.amazon.com/gp/help/200740930)
- [Removal FBA Order Details Reports](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110)
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
- [FBA Fee Preview Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Daily Inventory History Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Promotions Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Inventory Adjustments Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Received Inventory Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Inventory Event Detail Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Monthly Inventory History Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Manage Inventory](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Subscribe and Save Forecast Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Subscribe and Save Performance Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Flat File Archived Orders Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Flat File Returns Report by Return Date](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Canceled Listings Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Active Listings Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Open Listings Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Suppressed Listings Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Inactive Listings Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Stranded Inventory Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [XML Orders By Order Date Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Inventory Ledger Report - Detailed View](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Manage Inventory Health Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [Inventory Ledger Report - Summary View](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
- [FBA Reimbursements Report](https://sellercentral.amazon.com/help/hub/reference/G200732720)

## Report options

Make sure to configure the [required parameters](https://developer-docs.amazon.com/sp-api/docs/report-type-values) in the report options setting for the reports configured.

For `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL` and `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` streams maximum value for `period_in_days` 30 days and 60 days. 
So, for any value that exceeds the limit, the `period_in_days` will be automatically reduced to the limit for the stream.

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

| Version  | Date       | Pull Request                                               | Subject                                                                                                                                                                             |
|:---------|:-----------|:-----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `1.3.0`  | 2023-06-09 | [\#27110](https://github.com/airbytehq/airbyte/pull/27110) | Removed `app_id` from `InputConfiguration`, refactored `spec`  |
| `1.2.0`  | 2023-05-23 | [\#22503](https://github.com/airbytehq/airbyte/pull/22503) | Enabled stream attribute customization from Source configuration  |
| `1.1.0`  | 2023-04-21 | [\#23605](https://github.com/airbytehq/airbyte/pull/23605) | Add FBA Reimbursement Report stream   |
| `1.0.1`  | 2023-03-15 | [\#24098](https://github.com/airbytehq/airbyte/pull/24098) | Add Belgium Marketplace  |
| `1.0.0`  | 2023-03-13 | [\#23980](https://github.com/airbytehq/airbyte/pull/23980) | Make `app_id` required. Increase `end_date` gap up to 5 minutes from now for Finance streams. Fix connection check failure when trying to connect to Amazon Vendor Central accounts |
| `0.2.33` | 2023-03-01 | [\#23606](https://github.com/airbytehq/airbyte/pull/23606) | Implement reportOptions for all missing reports and refactor    |
| `0.2.32` | 2022-02-21 | [\#23300](https://github.com/airbytehq/airbyte/pull/23300) | Make AWS Access Key, AWS Secret Access and Role ARN optional    |
| `0.2.31` | 2022-01-10 | [\#16430](https://github.com/airbytehq/airbyte/pull/16430) | Implement slicing for report streams    |
| `0.2.30` | 2022-12-28 | [\#20896](https://github.com/airbytehq/airbyte/pull/20896) | Validate connections without orders data      |
| `0.2.29` | 2022-11-18 | [\#19581](https://github.com/airbytehq/airbyte/pull/19581) | Use user provided end date for GET_SALES_AND_TRAFFIC_REPORT   |
| `0.2.28` | 2022-10-20 | [\#18283](https://github.com/airbytehq/airbyte/pull/18283) | Added multiple (22) report types   |
| `0.2.26` | 2022-09-24 | [\#16629](https://github.com/airbytehq/airbyte/pull/16629) | Report API version to 2021-06-30, added multiple (5) report types  |
| `0.2.25` | 2022-07-27 | [\#15063](https://github.com/airbytehq/airbyte/pull/15063) | Add Restock Inventory Report |
| `0.2.24` | 2022-07-12 | [\#14625](https://github.com/airbytehq/airbyte/pull/14625) | Add FBA Storage Fees Report  |
| `0.2.23` | 2022-06-08 | [\#13604](https://github.com/airbytehq/airbyte/pull/13604) | Add new streams: Fullfiments returns and Settlement reports  |
| `0.2.22` | 2022-06-15 | [\#13633](https://github.com/airbytehq/airbyte/pull/13633) | Fix - handle start date for financial stream  |
| `0.2.21` | 2022-06-01 | [\#13364](https://github.com/airbytehq/airbyte/pull/13364) | Add financial streams  |
| `0.2.20` | 2022-05-30 | [\#13059](https://github.com/airbytehq/airbyte/pull/13059) | Add replication end date to config  |
| `0.2.19` | 2022-05-24 | [\#13119](https://github.com/airbytehq/airbyte/pull/13119) | Add OAuth2.0 support |
| `0.2.18` | 2022-05-06 | [\#12663](https://github.com/airbytehq/airbyte/pull/12663) | Add GET_XML_BROWSE_TREE_DATA report |
| `0.2.17` | 2022-05-19 | [\#12946](https://github.com/airbytehq/airbyte/pull/12946) | Add throttling exception managing in Orders streams  |
| `0.2.16` | 2022-05-04 | [\#12523](https://github.com/airbytehq/airbyte/pull/12523) | allow to use IAM user arn or IAM role |
| `0.2.15` | 2022-01-25 | [\#9789](https://github.com/airbytehq/airbyte/pull/9789)   | Add stream FbaReplacementsReports   |
| `0.2.14` | 2022-01-19 | [\#9621](https://github.com/airbytehq/airbyte/pull/9621)   | Add GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL report  |
| `0.2.13` | 2022-01-18 | [\#9581](https://github.com/airbytehq/airbyte/pull/9581)   | Change createdSince parameter to dataStartTime   |
| `0.2.12` | 2022-01-05 | [\#9312](https://github.com/airbytehq/airbyte/pull/9312)   | Add all remaining brand analytics report streams   |
| `0.2.11` | 2022-01-05 | [\#9115](https://github.com/airbytehq/airbyte/pull/9115)   | Fix reading only 100 orders    |
| `0.2.10` | 2021-12-31 | [\#9236](https://github.com/airbytehq/airbyte/pull/9236)   | Fix NoAuth deprecation warning   |
| `0.2.9`  | 2021-12-30 | [\#9212](https://github.com/airbytehq/airbyte/pull/9212)   | Normalize GET_SELLER_FEEDBACK_DATA header field names  |
| `0.2.8`  | 2021-12-22 | [\#8810](https://github.com/airbytehq/airbyte/pull/8810)   | Fix GET_SELLER_FEEDBACK_DATA Date cursor field format |
| `0.2.7`  | 2021-12-21 | [\#9002](https://github.com/airbytehq/airbyte/pull/9002)   | Extract REPORTS_MAX_WAIT_SECONDS to configurable parameter  |
| `0.2.6`  | 2021-12-10 | [\#8179](https://github.com/airbytehq/airbyte/pull/8179)   | Add GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT report  |
| `0.2.5`  | 2021-12-06 | [\#8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec   |
| `0.2.4`  | 2021-11-08 | [\#8021](https://github.com/airbytehq/airbyte/pull/8021)   | Added GET_SELLER_FEEDBACK_DATA report with incremental sync capability  |
| `0.2.3`  | 2021-11-08 | [\#7828](https://github.com/airbytehq/airbyte/pull/7828)   | Remove datetime format from all streams  |
| `0.2.2`  | 2021-11-08 | [\#7752](https://github.com/airbytehq/airbyte/pull/7752)   | Change `check_connection` function to use stream Orders  |
| `0.2.1`  | 2021-09-17 | [\#5248](https://github.com/airbytehq/airbyte/pull/5248)   | Added `extra stream` support. Updated `reports streams` logics   |
| `0.2.0`  | 2021-08-06 | [\#4863](https://github.com/airbytehq/airbyte/pull/4863)   | Rebuild source with `airbyte-cdk` |
| `0.1.3`  | 2021-06-23 | [\#4288](https://github.com/airbytehq/airbyte/pull/4288)   | Bugfix failing `connection check` |
| `0.1.2`  | 2021-06-15 | [\#4108](https://github.com/airbytehq/airbyte/pull/4108)   | Fixed: Sync fails with timeout when create report is CANCELLED` |
