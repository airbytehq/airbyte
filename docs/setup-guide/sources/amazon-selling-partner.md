# Amazon Selling Partner

This page contains the setup guide and reference information for the Amazon Selling Partner (SP).

## Prerequisites

* app\_id
* lwa\_app\_id
* lwa\_client\_secret
* refresh\_token
* aws\_access\_key
* aws\_secret\_key
* role\_arn
* aws\_environment
* region
* replication\_start\_date

## Setup guide

### Step 1: Set up Amazon Selling Partner

[Register](https://developer-docs.amazon.com/sp-api/docs/registering-your-application) Amazon Selling Partner application. [Create](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) IAM user.

### Step 2: Set up the Amazon Selling Partner data source

1. Select **Amazon Selling Partner** from the Source list.

2. Using developer application from Step 1, [generate refresh token](https://developer-docs.amazon.com/sp-api/docs/self-authorizationhttps://developer-docs.amazon.com/sp-api/docs/self-authorization).

3. Paste all data to required fields using your IAM user and developer account.

4. Click **Set up source**.

## Supported sync modes

The Amazon SP data source supports the following sync modes:

* Full Refresh
* Incremental

## Supported streams

This source is capable of syncing the following streams:

* [FBA Inventory Reports](https://sellercentral.amazon.com/gp/help/200740930)
* [FBA Orders Reports](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110)
* [FBA Shipments Reports](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989100)
* [FBA Replacements Reports](https://sellercentral.amazon.com/help/hub/reference/200453300)
* [FBA Storage Fees Report](https://sellercentral.amazon.com/help/hub/reference/G202086720)
* [Restock Inventory Reports](https://sellercentral.amazon.com/help/hub/reference/202105670)
* [Flat File Open Listings Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [Flat File Orders Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [Flat File Orders Reports By Last Update](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference) (incremental)
* [Amazon-Fulfilled Shipments Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [Merchant Listings Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [Vendor Direct Fulfillment Shipping](https://developer-docs.amazon.com/sp-api/docs/vendor-direct-fulfillment-shipping-api-v1-reference)
* [Vendor Inventory Health Reports](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [Orders](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference) (incremental)
* [Seller Feedback Report](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference) (incremental)
* [Brand Analytics Alternate Purchase Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [Brand Analytics Item Comparison Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [Brand Analytics Market Basket Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [Brand Analytics Repeat Purchase Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [Brand Analytics Search Terms Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [Browse tree report](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#browse-tree-report)
* [Financial Event Groups](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialeventgroups)
* [Financial Events](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialevents)

## Report options

Make sure to configure the [required parameters](https://developer-docs.amazon.com/sp-api/docs/report-type-values) in the report options setting for the reports configured.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| string | string |
| int, float, number | number |
| date | date |
| datetime | datetime |
| array | array |
| object | object |