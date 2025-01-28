# Amazon Seller Partner

<HideInUI>

This page contains the setup guide and reference information for the [Amazon Seller Partner](https://developer.amazonservices.com/) source connector.

</HideInUI>

## Prerequisites

- Amazon Seller Partner account

<!-- env:cloud -->

**For Airbyte Cloud:**

- AWS Environment
- AWS Region
- AWS Seller Partner Account Type
- Granted OAuth access

<!-- /env:cloud -->

<!-- env:oss -->

**For Airbyte Open Source:**

- AWS Environment
- AWS Region
- AWS Seller Partner Account Type
- LWA Client Id
- LWA Client Secret
- Refresh Token

<!-- /env:oss -->

## Setup guide

## Step 1: Set up Amazon Seller Partner

[Register](https://sellercentral.amazon.com/) your Amazon Seller Partner account.

<!-- env:oss -->

**Airbyte Open Source setup steps**

- [Register](https://developer-docs.amazon.com/sp-api/docs/registering-your-application) Amazon Seller Partner application. The application must be published as Amazon does not allow external parties such as Airbyte to access draft applications.

<!-- /env:oss -->

## Step 2: Set up the source connector in Airbyte

To pass the check for Seller and Vendor accounts, you must have access to the [Orders endpoint](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference) and the [Vendor Orders endpoint](https://developer-docs.amazon.com/sp-api/docs/vendor-orders-api-v1-reference#get-vendorordersv1purchaseorders), respectively.

<!-- env:cloud -->

#### For Airbyte Cloud:

1. [Log into your Airbyte Cloud](https://cloud.airbyte.com/workspaces) account.
2. Click Sources and then click + New source.
3. On the Set up the source page, select Amazon Seller Partner from the Source type dropdown.
4. Enter a name for the Amazon Seller Partner connector.
5. Click `Authenticate your account`.
6. Log in and Authorize to your Amazon Seller Partner account.
7. For `Start Date`, enter the date in `YYYY-MM-DD` format. The data added on and after this date will be replicated. This field is optional - if not provided or older than 2 years ago from today, the date 2 years ago from today will be used.
8. For `End Date`, enter the date in `YYYY-MM-DD` format. Any data after this date will not be replicated. This field is optional - if not provided, today's date will be used.
9. You can specify report options for each stream using **Report Options** section. Available options can be found in corresponding category [here](https://developer-docs.amazon.com/sp-api/docs/report-type-values).
10. For `Wait between requests to avoid fatal statuses in reports`, enable if you want to use wating time between requests to avoid fatal statuses in report based streams.
11. Click `Set up source`.

<!-- /env:cloud -->

<!-- env:oss -->

#### For Airbyte Open Source:

1. Navigate to the Airbyte Open Source dashboard.
2. On the Set up the source page, select Amazon Seller Partner from the Source type dropdown. 
3. Enter a name for the Amazon Seller Partner connector. 
4. Using developer application from Step 1, [generate](https://developer-docs.amazon.com/sp-api/docs/self-authorization) refresh token.
5. For Start Date, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated. This field is optional - if not provided, the date 2 years ago from today will be used.
6. For End Date, enter the date in YYYY-MM-DD format. Any data after this date will not be replicated. This field is optional - if not provided, today's date will be used.
7. You can specify report options for each stream using **Report Options** section. Available options can be found in corresponding category [here](https://developer-docs.amazon.com/sp-api/docs/report-type-values).
8. For `Wait between requests to avoid fatal statuses in reports`, enable if you want to use wating time between requests to avoid fatal statuses in report based streams.
9. Click `Set up source`.

<!-- /env:oss -->

## Supported sync modes

The Amazon Seller Partner source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts/#connection-sync-modes):

- Full Refresh
- Incremental

## Supported Streams

- [Active Listings Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory) \(incremental\)
- [All Listings Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory) \(incremental\)
- [Browse Tree Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-browse-tree) \(incremental\)
- [Canceled Listings Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory) \(incremental\)
- [FBA Amazon Fulfilled Inventory Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [FBA Amazon Fulfilled Shipments Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-sales-reports) \(incremental\)
- [FBA Fee Preview Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-payments-reports) \(incremental\)
- [FBA Manage Inventory](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [FBA Manage Inventory Health Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [FBA Multi-Country Inventory Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [FBA Promotions Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-sales-reports) \(incremental\)
- [FBA Reimbursements Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-payments-reports) \(incremental\)
- [FBA Removal Order Detail Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-removals-reports) \(incremental\)
- [FBA Removal Shipment Detail Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-removals-reports) \(incremental\)
- [FBA Replacements Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-concessions-reports) \(incremental\)
- [FBA Returns Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-concessions-reports) \(incremental\)
- [FBA Storage Fees Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [FBA Stranded Inventory Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [Financial Events](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialevents) \(incremental\)
- [Financial Event Groups](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialeventgroups) \(incremental\)
- [Flat File Archived Orders Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#order-tracking-reports) \(incremental\)
- [Flat File Feedback Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-performance) \(incremental\)
- [Flat File Orders By Last Update Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#order-tracking-reports) \(incremental\)
- [Flat File Orders By Order Date Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#order-tracking-reports) \(incremental\)
- [Flat File Returns Report by Return Date](https://developer-docs.amazon.com/sp-api/docs/report-type-values-returns) \(incremental\)
- [Flat File Settlement Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-settlement) \(incremental\)
- [Inactive Listings Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory) \(incremental\)
- [Inventory Ledger Report - Detailed View](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [Inventory Ledger Report - Summary View](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [Inventory Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory) \(incremental\)
- [Open Listings Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory) \(incremental\)
- [Orders](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference) \(incremental\)
- [Order Items](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference#getorderitems) \(incremental\)
- [Restock Inventory Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-inventory-reports) \(incremental\)
- [Scheduled XML Order Report (Shipping)](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#order-reports) \(incremental\)
- [Subscribe and Save Forecast Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-subscribe-and-save-reports) \(incremental\)
- [Subscribe and Save Performance Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-fba#fba-subscribe-and-save-reports) \(incremental\)
- [Suppressed Listings Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-inventory) \(incremental\)
- [Unshipped Orders Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#order-reports) \(incremental\)
- [Vendor Direct Fulfillment Shipping](https://developer-docs.amazon.com/sp-api/docs/vendor-direct-fulfillment-shipping-api-v1-reference) \(incremental\)
- [Vendor Forecasting Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-retail-analytics-reports) \(full-refresh\)
- [Vendor Orders](https://developer-docs.amazon.com/sp-api/docs/vendor-orders-api-v1-reference#get-vendorordersv1purchaseorders) \(incremental\)
- [XML Orders By Order Date Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-order#order-tracking-reports) \(incremental\)
<!-- env:oss -->
- [Amazon Search Terms Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#brand-analytics-reports) \(only available in OSS, incremental\)
- [Market Basket Analysis Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#brand-analytics-reports) \(only available in OSS, incremental\)
- [Net Pure Product Margin Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-retail-analytics-reports) \(only available in OSS, incremental\)
- [Rapid Retail Analytics Inventory Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-retail-analytics-reports) \(only available in OSS, incremental\)
- [Repeat Purchase](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#brand-analytics-reports) \(only available in OSS, incremental\)
- [Sales and Traffic Business Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#seller-retail-analytics-reports) \(only available in OSS, incremental\)
- [Vendor Inventory Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-retail-analytics-reports) \(only available in OSS, incremental\)
- [Vendor Sales Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-retail-analytics-reports) \(only available in OSS, incremental\)
- [Vendor Traffic Report](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics#vendor-retail-analytics-reports) \(only available in OSS, incremental\)
<!-- /env:oss -->

<HideInUI>

### Entity-Relationship Diagram (ERD)
<EntityRelationshipDiagram></EntityRelationshipDiagram>
</HideInUI>

## Report options

Report options can be assigned on a per-stream basis that alter the behavior when generating a report.
For the full list, refer to Amazon’s report type values [documentation](https://developer-docs.amazon.com/sp-api/docs/report-type-values).

Certain report types have required parameters that must be defined.
For the `GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL`, `GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL`, and `GET_FLAT_FILE_RETURNS_DATA_BY_RETURN_DATE` streams, the maximum allowable value for `period_in_days` is 30 days, 30 days, and 60 days, respectively. 
If the specified `period_in_days` exceeds these limits, it will be automatically adjusted to the maximum value for the respective stream, or set to 365 days if not provided.

For the Vendor Forecasting Report, we have two streams - `GET_VENDOR_FORECASTING_FRESH_REPORT` and `GET_VENDOR_FORECASTING_RETAIL_REPORT` which use the same `GET_VENDOR_FORECASTING_REPORT` Amazon's report,
but with different options for the `sellingProgram` parameter - `FRESH` and `RETAIL` respectively.

## Performance considerations

Information about rate limits you may find [here](https://developer-docs.amazon.com/sp-api/docs/usage-plans-and-rate-limits-in-the-sp-api).

## Data type map

| Integration Type         | Airbyte Type |
|:-------------------------|:-------------|
| `string`                 | `string`     |
| `int`, `float`, `number` | `number`     |
| `date`                   | `date`       |
| `datetime`               | `datetime`   |
| `array`                  | `array`      |
| `object`                 | `object`     |

## Limitations & Troubleshooting

### Failed to retrieve the report

```
Failed to retrieve the report 'YOUR_REPORT_NAME' for period 2024-01-01T12:01:15Z-2024-01-15T12:01:14Z. 
This will be read during the next sync. Report ID: YOUR_REPORT_ID. Error: Failed to retrieve the report result document.
```

Requesting reports via Amazon Seller Partner API can lead to failed syncs with error above "Failed to retrieve the report...".

One of the reasons why users face this issue is that report requests were made too often. 

**Solution 1:**

To overcome it you can force use sleeping between requests to avoid fatal statuses while requesting reports.

Steps:
1. Go to the Set Up page of the connector.
2. Open optional section.
3. Enable `Wait between requests to avoid fatal statuses in reports` toggle.

Disadvantages of this approach is that syncs with waiting between requests are much slower than without it. So it is better to create a separate connection only for stream that usually fails with "Failed to retrieve the report..." error. This will help you to avoid affecting streams that worked as expected.

:::note

For now the waiting logic only work for the following streams:
- GET_AMAZON_FULFILLED_SHIPMENTS_DATA_GENERAL
- GET_AFN_INVENTORY_DATA
- GET_FBA_ESTIMATED_FBA_FEES_TXT_DATA

:::

**Solution 2:**

Create a separate connection for streams which usually fail with error above "Failed to retrieve the report..." and disable sync of these streams in the first connection with streams which don't fail because of the error. Adjust the sync time of these two connection to do not overlap. It's recommended to have a time break between syncs in the connections.


## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                              | Subject                                                                                                                                                                             |
|:-----------|:-----------|:----------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 4.5.0-rc.2 | 2025-01-28 | [52592](https://github.com/airbytehq/airbyte/pull/52592)  | Only request data for the `Orders` stream for up to 2 minutes before present if replication_start_date is not specified                                                             |
| 4.5.0-rc.1 | 2025-01-27 | [49293](https://github.com/airbytehq/airbyte/pull/49293)  | Convert to REST and reports streams to concurrent low-code CDK in v6. Remove buggy analytics streams                                                                                |
| 4.4.7      | 2024-11-14 | [47691](https://github.com/airbytehq/airbyte/pull/47691)  | Fix `period_in_days` definition                                                                                                                                                     |
| 4.4.6      | 2024-11-25 | [48644](https://github.com/airbytehq/airbyte/pull/48644)  | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64              |
| 4.4.5      | 2024-11-04 | [47049](https://github.com/airbytehq/airbyte/pull/47049)  | Update dependencies                                                                                                                                                                 |
| 4.4.4      | 2024-10-12 | [46817](https://github.com/airbytehq/airbyte/pull/46817)  | Update dependencies                                                                                                                                                                 |
| 4.4.3      | 2024-10-05 | [46473](https://github.com/airbytehq/airbyte/pull/46473)  | Update dependencies                                                                                                                                                                 |
| 4.4.2      | 2024-09-28 | [44748](https://github.com/airbytehq/airbyte/pull/44748)  | Update dependencies                                                                                                                                                                 |
| 4.4.1      | 2024-08-17 | [43739](https://github.com/airbytehq/airbyte/pull/43739)  | Update dependencies                                                                                                                                                                 |
| 4.4.0      | 2024-07-17 | [42052](https://github.com/airbytehq/airbyte/pull/42052)  | Add waiting between requests logic to avoid failed report requests                                                                                                                  |
| 4.3.11     | 2024-07-13 | [41873](https://github.com/airbytehq/airbyte/pull/41873)  | Update dependencies                                                                                                                                                                 |
| 4.3.10     | 2024-07-10 | [41345](https://github.com/airbytehq/airbyte/pull/41345)  | Update dependencies                                                                                                                                                                 |
| 4.3.9      | 2024-07-09 | [41158](https://github.com/airbytehq/airbyte/pull/41158)  | Update dependencies                                                                                                                                                                 |
| 4.3.8      | 2024-07-08 | [40751](https://github.com/airbytehq/airbyte/pull/40751)  | Improve error messaging and turning on alerting                                                                                                                                     |
| 4.3.7      | 2024-07-06 | [40990](https://github.com/airbytehq/airbyte/pull/40990)  | Update dependencies                                                                                                                                                                 |
| 4.3.6      | 2024-07-01 | [40590](https://github.com/airbytehq/airbyte/pull/40590)  | Add log message when data only accessible to seller accounts, add report id in log message for fatal report status, add check for start date.                                       |
| 4.3.5      | 2024-06-27 | [40215](https://github.com/airbytehq/airbyte/pull/40215)  | Replaced deprecated AirbyteLogger with logging.Logger                                                                                                                               |
| 4.3.4      | 2024-06-25 | [40384](https://github.com/airbytehq/airbyte/pull/40384)  | Update dependencies                                                                                                                                                                 |
| 4.3.3      | 2024-06-22 | [40008](https://github.com/airbytehq/airbyte/pull/40008)  | Update dependencies                                                                                                                                                                 |
| 4.3.2      | 2024-06-13 | [39441](https://github.com/airbytehq/airbyte/pull/39441)  | Update state handling for incremental streams                                                                                                                                       |
| 4.3.1      | 2024-06-04 | [38969](https://github.com/airbytehq/airbyte/pull/38969)  | [autopull] Upgrade base image to v1.2.1                                                                                                                                             |
| 4.3.0      | 2024-05-24 | [#38657](https://github.com/airbytehq/airbyte/pull/38657) | Extend the report_options spec config with a `stream_name` attribute                                                                                                                |
| 4.2.4      | 2024-05-15 | [#38210](https://github.com/airbytehq/airbyte/pull/38210) | Fix `GET_VENDOR_TRAFFIC_REPORT` stream with report option `reportPeriod=DAY`                                                                                                        |
| 4.2.3      | 2024-05-09 | [#38078](https://github.com/airbytehq/airbyte/pull/38078) | Hide OSS-only streams in report options config for cloud users                                                                                                                      |
| 4.2.2      | 2024-04-24 | [#36630](https://github.com/airbytehq/airbyte/pull/36630) | Schema descriptions and CDK 0.80.0                                                                                                                                                  |
| 4.2.1      | 2024-04-08 | [#36895](https://github.com/airbytehq/airbyte/pull/36895) | Fix `reportPeriod` day query params                                                                                                                                                 |
| 4.2.0      | 2024-03-19 | [#36267](https://github.com/airbytehq/airbyte/pull/36267) | Pin airbyte-cdk version to `^0`                                                                                                                                                     |
| 4.1.0      | 2024-03-12 | [#35954](https://github.com/airbytehq/airbyte/pull/35954) | Add `GET_VENDOR_FORECASTING_FRESH_REPORT` and `GET_VENDOR_FORECASTING_RETAIL_REPORT` streams                                                                                        |
| 4.0.0      | 2024-02-23 | [#35439](https://github.com/airbytehq/airbyte/pull/35439) | Update schema for the `GET_FBA_STORAGE_FEE_CHARGES_DATA` stream                                                                                                                     |
| 3.5.0      | 2024-02-09 | [#35331](https://github.com/airbytehq/airbyte/pull/35331) | Fix check for Vendor accounts. Add failed report result message                                                                                                                     |
| 3.4.0      | 2024-02-15 | [#35273](https://github.com/airbytehq/airbyte/pull/35273) | Add `VendorOrders` stream                                                                                                                                                           |
| 3.3.2      | 2024-02-13 | [#33996](https://github.com/airbytehq/airbyte/pull/33996) | Add integration tests                                                                                                                                                               |
| 3.3.1      | 2024-02-09 | [#35106](https://github.com/airbytehq/airbyte/pull/35106) | Add logs for the failed check command                                                                                                                                               |
| 3.3.0      | 2024-02-09 | [#35062](https://github.com/airbytehq/airbyte/pull/35062) | Fix the check command for the `Vendor` account type                                                                                                                                 |
| 3.2.2      | 2024-02-07 | [#34914](https://github.com/airbytehq/airbyte/pull/34914) | Fix date formatting for ledger reports with aggregation by month                                                                                                                    |
| 3.2.1      | 2024-01-30 | [#34654](https://github.com/airbytehq/airbyte/pull/34654) | Fix date format in state message for streams with custom dates formatting                                                                                                           |
| 3.2.0      | 2024-01-26 | [#34549](https://github.com/airbytehq/airbyte/pull/34549) | Update schemas for vendor analytics streams                                                                                                                                         |
| 3.1.0      | 2024-01-17 | [#34283](https://github.com/airbytehq/airbyte/pull/34283) | Delete deprecated streams                                                                                                                                                           |
| 3.0.1      | 2023-12-22 | [#33741](https://github.com/airbytehq/airbyte/pull/33741) | Improve report streams performance                                                                                                                                                  |
| 3.0.0      | 2023-12-12 | [#32977](https://github.com/airbytehq/airbyte/pull/32977) | Make all streams incremental                                                                                                                                                        |
| 2.5.0      | 2023-11-27 | [#32505](https://github.com/airbytehq/airbyte/pull/32505) | Make report options configurable via UI                                                                                                                                             |
| 2.4.0      | 2023-11-23 | [#32738](https://github.com/airbytehq/airbyte/pull/32738) | Add `GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT`, `GET_VENDOR_REAL_TIME_INVENTORY_REPORT`, and `GET_VENDOR_TRAFFIC_REPORT` streams                                                   |
| 2.3.0      | 2023-11-22 | [#32541](https://github.com/airbytehq/airbyte/pull/32541) | Make `GET_AFN_INVENTORY_DATA`, `GET_AFN_INVENTORY_DATA_BY_COUNTRY`, and `GET_V2_SETTLEMENT_REPORT_DATA_FLAT_FILE` streams incremental                                               |
| 2.2.0      | 2023-11-21 | [#32639](https://github.com/airbytehq/airbyte/pull/32639) | Make start date optional, if start date is not provided, date 2 years ago from today will be used                                                                                   |
| 2.1.1      | 2023-11-21 | [#32560](https://github.com/airbytehq/airbyte/pull/32560) | Silently exit sync if the retry attempts were unsuccessful                                                                                                                          |
| 2.1.0      | 2023-11-21 | [#32591](https://github.com/airbytehq/airbyte/pull/32591) | Add new fields to GET_LEDGER_DETAIL_VIEW_DATA, GET_FBA_INVENTORY_PLANNING_DATA and Orders schemas                                                                                   |
| 2.0.2      | 2023-11-17 | [#32462](https://github.com/airbytehq/airbyte/pull/32462) | Remove Max time option from specification; set default waiting time for reports to 1 hour                                                                                           |
| 2.0.1      | 2023-11-16 | [#32550](https://github.com/airbytehq/airbyte/pull/32550) | Fix the OAuth flow                                                                                                                                                                  |
| 2.0.0      | 2023-11-23 | [#32355](https://github.com/airbytehq/airbyte/pull/32355) | Remove Brand Analytics from Airbyte Cloud, permanently remove deprecated FBA reports                                                                                                |
| 1.6.2      | 2023-11-14 | [#32508](https://github.com/airbytehq/airbyte/pull/32508) | Do not use AWS signature as it is no longer required by the Amazon API                                                                                                              |
| 1.6.1      | 2023-11-13 | [#32457](https://github.com/airbytehq/airbyte/pull/32457) | Fix report decompression                                                                                                                                                            |
| 1.6.0      | 2023-11-09 | [#32259](https://github.com/airbytehq/airbyte/pull/32259) | Mark "aws_secret_key" and "aws_access_key" as required in specification; update schema for stream `Orders`                                                                          |
| 1.5.1      | 2023-08-18 | [#29255](https://github.com/airbytehq/airbyte/pull/29255) | Field role_arn is optional on UI but not really on the backend blocking connector set up using oauth                                                                                |
| 1.5.0      | 2023-08-08 | [#29054](https://github.com/airbytehq/airbyte/pull/29054) | Add new stream `OrderItems`                                                                                                                                                         |
| 1.4.1      | 2023-07-25 | [#27050](https://github.com/airbytehq/airbyte/pull/27050) | Fix - non vendor accounts connector create/check issue                                                                                                                              |
| 1.4.0      | 2023-07-21 | [#27110](https://github.com/airbytehq/airbyte/pull/27110) | Add `GET_FLAT_FILE_ACTIONABLE_ORDER_DATA_SHIPPING` and `GET_ORDER_REPORT_DATA_SHIPPING` streams                                                                                     |
| 1.3.0      | 2023-06-09 | [#27110](https://github.com/airbytehq/airbyte/pull/27110) | Removed `app_id` from `InputConfiguration`, refactored `spec`                                                                                                                       |
| 1.2.0      | 2023-05-23 | [#22503](https://github.com/airbytehq/airbyte/pull/22503) | Enabled stream attribute customization from Source configuration                                                                                                                    |
| 1.1.0      | 2023-04-21 | [#23605](https://github.com/airbytehq/airbyte/pull/23605) | Add FBA Reimbursement Report stream                                                                                                                                                 |
| 1.0.1      | 2023-03-15 | [#24098](https://github.com/airbytehq/airbyte/pull/24098) | Add Belgium Marketplace                                                                                                                                                             |
| 1.0.0      | 2023-03-13 | [#23980](https://github.com/airbytehq/airbyte/pull/23980) | Make `app_id` required. Increase `end_date` gap up to 5 minutes from now for Finance streams. Fix connection check failure when trying to connect to Amazon Vendor Central accounts |
| 0.2.33     | 2023-03-01 | [#23606](https://github.com/airbytehq/airbyte/pull/23606) | Implement reportOptions for all missing reports and refactor                                                                                                                        |
| 0.2.32     | 2022-02-21 | [#23300](https://github.com/airbytehq/airbyte/pull/23300) | Make AWS Access Key, AWS Secret Access and Role ARN optional                                                                                                                        |
| 0.2.31     | 2022-01-10 | [#16430](https://github.com/airbytehq/airbyte/pull/16430) | Implement slicing for report streams                                                                                                                                                |
| 0.2.30     | 2022-12-28 | [#20896](https://github.com/airbytehq/airbyte/pull/20896) | Validate connections without orders data                                                                                                                                            |
| 0.2.29     | 2022-11-18 | [#19581](https://github.com/airbytehq/airbyte/pull/19581) | Use user provided end date for GET_SALES_AND_TRAFFIC_REPORT                                                                                                                         |
| 0.2.28     | 2022-10-20 | [#18283](https://github.com/airbytehq/airbyte/pull/18283) | Added multiple (22) report types                                                                                                                                                    |
| 0.2.26     | 2022-09-24 | [#16629](https://github.com/airbytehq/airbyte/pull/16629) | Report API version to 2021-06-30, added multiple (5) report types                                                                                                                   |
| 0.2.25     | 2022-07-27 | [#15063](https://github.com/airbytehq/airbyte/pull/15063) | Add Restock Inventory Report                                                                                                                                                        |
| 0.2.24     | 2022-07-12 | [#14625](https://github.com/airbytehq/airbyte/pull/14625) | Add FBA Storage Fees Report                                                                                                                                                         |
| 0.2.23     | 2022-06-08 | [#13604](https://github.com/airbytehq/airbyte/pull/13604) | Add new streams: Fullfiments returns and Settlement reports                                                                                                                         |
| 0.2.22     | 2022-06-15 | [#13633](https://github.com/airbytehq/airbyte/pull/13633) | Fix - handle start date for financial stream                                                                                                                                        |
| 0.2.21     | 2022-06-01 | [#13364](https://github.com/airbytehq/airbyte/pull/13364) | Add financial streams                                                                                                                                                               |
| 0.2.20     | 2022-05-30 | [#13059](https://github.com/airbytehq/airbyte/pull/13059) | Add replication end date to config                                                                                                                                                  |
| 0.2.19     | 2022-05-24 | [#13119](https://github.com/airbytehq/airbyte/pull/13119) | Add OAuth2.0 support                                                                                                                                                                |
| 0.2.18     | 2022-05-06 | [#12663](https://github.com/airbytehq/airbyte/pull/12663) | Add GET_XML_BROWSE_TREE_DATA report                                                                                                                                                 |
| 0.2.17     | 2022-05-19 | [#12946](https://github.com/airbytehq/airbyte/pull/12946) | Add throttling exception managing in Orders streams                                                                                                                                 |
| 0.2.16     | 2022-05-04 | [#12523](https://github.com/airbytehq/airbyte/pull/12523) | Allow to use IAM user arn or IAM role                                                                                                                                               |
| 0.2.15     | 2022-01-25 | [#9789](https://github.com/airbytehq/airbyte/pull/9789)   | Add stream FbaReplacementsReports                                                                                                                                                   |
| 0.2.14     | 2022-01-19 | [#9621](https://github.com/airbytehq/airbyte/pull/9621)   | Add GET_FLAT_FILE_ALL_ORDERS_DATA_BY_LAST_UPDATE_GENERAL report                                                                                                                     |
| 0.2.13     | 2022-01-18 | [#9581](https://github.com/airbytehq/airbyte/pull/9581)   | Change createdSince parameter to dataStartTime                                                                                                                                      |
| 0.2.12     | 2022-01-05 | [#9312](https://github.com/airbytehq/airbyte/pull/9312)   | Add all remaining brand analytics report streams                                                                                                                                    |
| 0.2.11     | 2022-01-05 | [#9115](https://github.com/airbytehq/airbyte/pull/9115)   | Fix reading only 100 orders                                                                                                                                                         |
| 0.2.10     | 2021-12-31 | [#9236](https://github.com/airbytehq/airbyte/pull/9236)   | Fix NoAuth deprecation warning                                                                                                                                                      |
| 0.2.9      | 2021-12-30 | [#9212](https://github.com/airbytehq/airbyte/pull/9212)   | Normalize GET_SELLER_FEEDBACK_DATA header field names                                                                                                                               |
| 0.2.8      | 2021-12-22 | [#8810](https://github.com/airbytehq/airbyte/pull/8810)   | Fix GET_SELLER_FEEDBACK_DATA Date cursor field format                                                                                                                               |
| 0.2.7      | 2021-12-21 | [#9002](https://github.com/airbytehq/airbyte/pull/9002)   | Extract REPORTS_MAX_WAIT_SECONDS to configurable parameter                                                                                                                          |
| 0.2.6      | 2021-12-10 | [#8179](https://github.com/airbytehq/airbyte/pull/8179)   | Add GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT report                                                                                                                                  |
| 0.2.5      | 2021-12-06 | [#8425](https://github.com/airbytehq/airbyte/pull/8425)   | Update title, description fields in spec                                                                                                                                            |
| 0.2.4      | 2021-11-08 | [#8021](https://github.com/airbytehq/airbyte/pull/8021)   | Added GET_SELLER_FEEDBACK_DATA report with incremental sync capability                                                                                                              |
| 0.2.3      | 2021-11-08 | [#7828](https://github.com/airbytehq/airbyte/pull/7828)   | Remove datetime format from all streams                                                                                                                                             |
| 0.2.2      | 2021-11-08 | [#7752](https://github.com/airbytehq/airbyte/pull/7752)   | Change `check_connection` function to use stream Orders                                                                                                                             |
| 0.2.1      | 2021-09-17 | [#5248](https://github.com/airbytehq/airbyte/pull/5248)   | Added `extra stream` support. Updated `reports streams` logics                                                                                                                      |
| 0.2.0      | 2021-08-06 | [#4863](https://github.com/airbytehq/airbyte/pull/4863)   | Rebuild source with `airbyte-cdk`                                                                                                                                                   |
| 0.1.3      | 2021-06-23 | [#4288](https://github.com/airbytehq/airbyte/pull/4288)   | Bugfix failing `connection check`                                                                                                                                                   |
| 0.1.2      | 2021-06-15 | [#4108](https://github.com/airbytehq/airbyte/pull/4108)   | Fixed: Sync fails with timeout when create report is CANCELLED`                                                                                                                     |

</details>
