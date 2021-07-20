# Cart

## Sync overview

This source can sync data for the [Cart API](https://developers.cart.com/docs/rest-api/docs/README.md). All streams we support are Incremental sync.
You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

* [CustomersCart](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1customers/get) (Incremental)
* [Orders](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1orders/get) (Incremental)
* [OrderPayments](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_payments/get) (Incremental)
* [Products](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1products/get) (Incremental)

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

* Cart access_token

### Setup guide

Please follow these [steps](https://developers.cart.com/docs/rest-api/docs/README.md#setup) to obtain the access token for your account. 

## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-06-08 | [4574](https://github.com/airbytehq/airbyte/pull/4574) | Initial Release |