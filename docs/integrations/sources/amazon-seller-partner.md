# Amazon Seller Partner

## Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |

This source syncs data from the [Amazon Seller Partner API](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

## Supported Tables

This source is capable of syncing the following streams:

* [Order Reports](https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780)
* [All Listings](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#inventory-reports)
* [FBA Inventory Reports](https://sellercentral.amazon.com/gp/help/200740930)
* [Amazon-Fulfilled Shipments Report](https://sellercentral.amazon.com/gp/help/help.html?itemID=200453120)
* [Open Listings Report](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#inventory-reports)
* [Removal Order Detail Report (overview)](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110)
* [Removal Shipment Detail Report](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989100)
* [Inventory Health & Planning Report](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#vendor-retail-analytics-reports)
* [Orders](https://github.com/amzn/selling-partner-api-docs/blob/main/references/orders-api/ordersV0.md) \(incremental\)
* [VendorDirectFulfillmentShipping](https://github.com/amzn/selling-partner-api-docs/blob/main/references/vendor-direct-fulfillment-shipping-api/vendorDirectFulfillmentShippingV1.md)
* [Seller Feedback Report](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#performance-reports)
* [Brand Analytics Search Terms Report](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#brand-analytics-reports)

## Getting started

**Requirements**

* replication\_start\_date
* refresh\_token
* lwa\_app\_id
* lwa\_client\_secret
* aws\_access\_key
* aws\_secret\_key
* role\_arn
* aws\_environment
* region

**Setup guide**

Information about how to get credentials you may find [here](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

## Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `int`, `float`, `number` | `number` |  |
| `date` | `date` |  |
| `datetime` | `datetime` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Performance Considerations (Airbyte Open-Source)

Information about rate limits you may find [here](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/usage-plans-rate-limits/Usage-Plans-and-Rate-Limits.md).


## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| `0.2.9` | 2021-12-30 | [\#9212](https://github.com/airbytehq/airbyte/pull/9212) | Normalize GET_SELLER_FEEDBACK_DATA header field names |
| `0.2.8` | 2021-12-22 | [\#8810](https://github.com/airbytehq/airbyte/pull/8810) | Fix GET_SELLER_FEEDBACK_DATA Date cursor field format |
| `0.2.7` | 2021-12-21 | [\#9002](https://github.com/airbytehq/airbyte/pull/9002) | Extract REPORTS_MAX_WAIT_SECONDS to configurable parameter |
| `0.2.6` | 2021-12-10 | [\#8179](https://github.com/airbytehq/airbyte/pull/8179) | Add GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT report |
| `0.2.5` | 2021-12-06 | [\#8425](https://github.com/airbytehq/airbyte/pull/8425) | Update title, description fields in spec |
| `0.2.4` | 2021-11-08 | [\#8021](https://github.com/airbytehq/airbyte/pull/8021) | Added GET_SELLER_FEEDBACK_DATA report with incremental sync capability |
| `0.2.3` | 2021-11-08 | [\#7828](https://github.com/airbytehq/airbyte/pull/7828) | Remove datetime format from all streams |
| `0.2.2` | 2021-11-08 | [\#7752](https://github.com/airbytehq/airbyte/pull/7752) | Change `check_connection` function to use stream Orders |
| `0.2.1` | 2021-09-17 | [\#5248](https://github.com/airbytehq/airbyte/pull/5248) | `Added extra stream support. Updated reports streams logics` |
| `0.2.0` | 2021-08-06 | [\#4863](https://github.com/airbytehq/airbyte/pull/4863) | `Rebuild source with airbyte-cdk` |
| `0.1.3` | 2021-06-23 | [\#4288](https://github.com/airbytehq/airbyte/pull/4288) | `Bugfix failing connection check` |
| `0.1.2` | 2021-06-15 | [\#4108](https://github.com/airbytehq/airbyte/pull/4108) | `Fixed: Sync fails with timeout when create report is CANCELLED` |
