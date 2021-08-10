# Amazon Seller Partner

## Sync overview

This source can sync data for the [Amazon Seller Partner API](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

### Output schema

This source is capable of syncing the following streams:

* [Orders](https://github.com/amzn/selling-partner-api-docs/blob/main/references/orders-api/ordersV0.md) (incremental)
* [GET_FLAT_FILE_ALL_ORDERS_DATA_BY_ORDER_DATE_GENERAL](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#order-tracking-reports) (incremental)
* [GET_MERCHANT_LISTINGS_ALL_DATA](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#inventory-reports) (incremental)
* [GET_FBA_INVENTORY_AGED_DATA](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#fulfillment-by-amazon-fba-reports) (incremental)


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

* replication_start_date
* refresh_token
* lwa_app_id
* lwa_client_secret
* aws_access_key
* aws_secret_key
* role_arn
* aws_environment
* region

### Setup guide

Information about how to get credentials you may find [here](https://github.com/amzn/selling-partner-api-docs/blob/main/guides/en-US/developer-guide/SellingPartnerApiDeveloperGuide.md).

## CHANGELOG

| Version | Date | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| `0.2.0` | 2021-08-06 | [#4863](https://github.com/airbytehq/airbyte/pull/4863) | `Rebuild source with airbyte-cdk` |
| `0.1.3` | 2021-06-23 | [#4288](https://github.com/airbytehq/airbyte/pull/4288) | `Bugfix failing connection check` |
| `0.1.2` | 2021-06-15 | [#4108](https://github.com/airbytehq/airbyte/pull/4108) | `Fixed: Sync fails with timeout when create report is CANCELLED` |
