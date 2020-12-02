# Braintree

## Sync overview

This source can sync data for the [Braintree API](https://developers.braintreepayments.com/start/overview).

This Source Connector is based on a [Singer Tap](https://github.com/singer-io/tap-braintree).

### Output schema

This Source is capable of syncing the following core Streams:

* [Transactions](https://developers.braintreepayments.com/reference/response/transaction/python)

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
| Full Refresh Sync | yes |  |
| Incremental Sync | no |  |

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