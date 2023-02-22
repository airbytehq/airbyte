# Amazon Seller Partner

This page contains the setup guide and reference information for Amazon Seller Partner (SP).

## Prerequisites

* Store Name
* App Id
* Amazon SP account
* AWS Access Key
* AWS Secret Access Key
* Role ARN
* AWS Environment
* AWS Region

## Setup guide

### Step 1: Set up Amazon Seller Partner

[Register](https://developer-docs.amazon.com/sp-api/docs/registering-your-application) Amazon Seller Partner application. [Create](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html) IAM user.

### Step 2: Set up the Amazon Seller Partner data source

1. Select **Amazon Seller Partner** from the Source list.

2. Enter a **Source Name**.

3. Enter your Amazon **Store Name**.

4. Enter your Amazon **App ID**.

5. **Authenticate your Amazon Seller Partner account**.

6. Enter your **AWS Access Key**.

7. Enter your **AWS Secret Access Key**.

8. Enter your **Role ARN**.

9. Select your **AWS Environment**.

10. **Max wait time for reports (in seconds)** is the maximum number of minutes the connector waits for the generation of a report for streams.

11. **Period In Days** will be used for stream slicing for initial full_refresh sync when no updated state is present for reports that support sliced incremental sync. 

12. Select your **AWS Region**.

13. **End Date (Optional)** - any data after this date will not be replicated.

14. **Start Date** - Any data before this date will not be replicated.

15. **Report Options** is additional information passed to reports. Must be a valid json string.

16. Click **Set up source**.

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
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |