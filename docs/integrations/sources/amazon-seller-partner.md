# Amazon Seller Partner

## Sync overview

This source can sync data for the [Amazon Seller Partner API](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

### Output schema

This source is capable of syncing the following streams:

* [GET\_FLAT\_FILE\_ALL\_ORDERS\_DATA\_BY\_ORDER\_DATE\_GENERAL](https://sellercentral.amazon.com/gp/help/help.html?itemID=201648780)
* [GET\_MERCHANT\_LISTINGS\_ALL\_DATA](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#inventory-reports)
* [GET\_FBA\_INVENTORY\_AGED\_DATA](https://sellercentral.amazon.com/gp/help/200740930)
* [GET\_AMAZON\_FULFILLED\_SHIPMENTS\_DATA\_GENERAL](https://sellercentral.amazon.com/gp/help/help.html?itemID=200453120)
* [GET\_FLAT\_FILE\_OPEN\_LISTINGS\_DATA](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#inventory-reports)
* [GET\_FBA\_FULFILLMENT\_REMOVAL\_ORDER\_DETAIL\_DATA](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110)
* [GET\_FBA\_FULFILLMENT\_REMOVAL\_SHIPMENT\_DETAIL\_DATA](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989100)
* [GET\_VENDOR\_INVENTORY\_HEALTH\_AND\_PLANNING\_REPORT](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#vendor-retail-analytics-reports)
* [Orders](https://github.com/amzn/selling-partner-api-docs/blob/main/references/orders-api/ordersV0.md) \(incremental\)
* [VendorDirectFulfillmentShipping](https://github.com/amzn/selling-partner-api-docs/blob/main/references/vendor-direct-fulfillment-shipping-api/vendorDirectFulfillmentShippingV1.md)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `int`, `float`, `number` | `number` |  |
| `date` | `date` |  |
| `datetime` | `datetime` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | yes |  |
| Incremental Sync | yes |  |
| Namespaces | No |  |

### Performance considerations

Information about rate limits you may find [here](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/usage-plans-rate-limits/Usage-Plans-and-Rate-Limits.md).

## Getting started

### Requirements

* replication\_start\_date
* refresh\_token
* lwa\_app\_id
* lwa\_client\_secret
* aws\_access\_key
* aws\_secret\_key
* role\_arn
* aws\_environment
* region

### Setup guide

Information about how to get credentials you may find [here](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| `0.2.1` | 2021-09-17 | [\#5248](https://github.com/airbytehq/airbyte/pull/5248) | `Added extra stream support. Updated reports streams logics` |
| `0.2.0` | 2021-08-06 | [\#4863](https://github.com/airbytehq/airbyte/pull/4863) | `Rebuild source with airbyte-cdk` |
| `0.1.3` | 2021-06-23 | [\#4288](https://github.com/airbytehq/airbyte/pull/4288) | `Bugfix failing connection check` |
| `0.1.2` | 2021-06-15 | [\#4108](https://github.com/airbytehq/airbyte/pull/4108) | `Fixed: Sync fails with timeout when create report is CANCELLED` |

