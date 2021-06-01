# Amazon Seller Partner

## Sync overview

This source can sync data for the [Amazon Seller Partner API](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

### Output schema

This source is capable of syncing the following streams:

* [Orders](https://github.com/amzn/selling-partner-api-docs/blob/main/references/orders-api/ordersV0.md)
* [GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reportType_string_array_values.md#order-tracking-reports)


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

* refresh_token
* lwa_app_id
* lwa_client_secret
* AWS USER ACCESS KEY
* AWS USER SECRET KEY
* role_arn

### Setup guide

Information about how to get credentials you may find [here](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

