# Braintree

## Sync overview

This source can sync data for the [Braintree API](https://developers.braintreepayments.com/start/overview). It supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://developer.paypal.com/braintree/docs/reference/request/customer/search)
* [Discounts](https://developer.paypal.com/braintree/docs/reference/response/discount)
* [Disputes](https://developer.paypal.com/braintree/docs/reference/request/dispute/search)
* [Transactions](https://developers.braintreepayments.com/reference/response/transaction/python)
* [Merchant Accounts](https://developer.paypal.com/braintree/docs/reference/response/merchant-account)
* [Plans](https://developer.paypal.com/braintree/docs/reference/response/plan)
* [Subscriptions](https://developer.paypal.com/braintree/docs/reference/response/subscription)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--- | :--- | :--- |
| `string` | `string` |  |
| `number` | `number` |  |
| `array` | `array` |  |
| `object` | `object` |  |

### Features

| Feature | Supported?\(Yes/No\) | Notes |
| :--- | :--- | :--- |
| Full Refresh Sync | Yes |  |
| Incremental Sync | Yes |  |
| Namespaces | No |  |

### Performance considerations

The connector is restricted by normal Braintree [requests limitation](https://developers.braintreepayments.com/reference/general/searching/search-results/python#search-limit) on search transactions.

The Braintree connector should not run into Braintree API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Braintree Merchant ID 
* Braintree Public Key 
* Braintree Private Key 
* Environment 

### Setup guide

Generate all requirements using the [Braintree documentation](https://articles.braintreepayments.com/control-panel/important-gateway-credentials).

We recommend creating a restricted, read-only key specifically for Airbyte access. This will allow you to control which resources Airbyte should be able to access.

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.2 | 2021-12-22 | [9042](https://github.com/airbytehq/airbyte/pull/9042) | Fix `$ref` in schema and spec |
| 0.1.1 | 2021-10-27 | [7432](https://github.com/airbytehq/airbyte/pull/7432) | Dispute model should accept multiple Evidences |
| 0.1.0 | 2021-08-17 | [5362](https://github.com/airbytehq/airbyte/pull/5362) | Initial version |

