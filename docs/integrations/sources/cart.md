# Cart

## Sync overview

This source can sync data for the [Cart API](https://developers.cart.com/docs/rest-api/docs/README.md). It supports both Full Refresh and Incremental sync for all streams.
You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [CustomersCart](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1customers/get)
* [Orders](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1orders/get)
* [OrderPayments](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_payments/get)
* [Products](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1products/get)

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

The Cart api has some request limitation. See [this](https://developers.cart.com/docs/rest-api/docs/README.md#rate-limiting) .

## Getting started

### Requirements

* AmeriCommerce account
* Admin access
* Access Token

### Setup guide

Please follow these [steps](https://developers.cart.com/docs/rest-api/docs/README.md#setup) to obtain Access Token for your account. 

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.2   | 2021-08-23 | [1111](https://github.com/airbytehq/airbyte/pull/1111) | Add `order_items` stream |
| 0.1.0   | 2021-06-08 | [4574](https://github.com/airbytehq/airbyte/pull/4574) | Initial Release |
