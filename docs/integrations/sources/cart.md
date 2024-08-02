# Cart.com

## Sync overview

This source can sync data for the [Cart.com API](https://developers.cart.com/docs/rest-api/docs/README.md). It supports both Full Refresh and Incremental sync for all streams. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

- [CustomersCart](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1customers/get)
- [Orders](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1orders/get)
- [OrderPayments](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_payments/get)
- [Products](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1products/get)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature           | Supported?\(Yes/No\) | Notes |
| :---------------- | :------------------- | :---- |
| Full Refresh Sync | Yes                  |       |
| Incremental Sync  | Yes                  |       |
| Namespaces        | No                   |       |

### Performance considerations

The Cart.com API has some request limitation. See [this](https://developers.cart.com/docs/rest-api/docs/README.md#rate-limiting) .

## Getting started

### Requirements

- AmeriCommerce account
- Admin access
- Access Token

### Setup guide

Please follow these [steps](https://developers.cart.com/docs/rest-api/docs/README.md#setup) to obtain Access Token for your account.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| 0.3.6 | 2024-06-29 | [40011](https://github.com/airbytehq/airbyte/pull/40011) | Update dependencies |
| 0.3.5 | 2024-04-19 | [37131](https://github.com/airbytehq/airbyte/pull/37131) | Updating to 0.80.0 CDK |
| 0.3.4 | 2024-04-18 | [37131](https://github.com/airbytehq/airbyte/pull/37131) | Manage dependencies with Poetry. |
| 0.3.3 | 2024-04-15 | [37131](https://github.com/airbytehq/airbyte/pull/37131) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.3.2 | 2024-04-12 | [37131](https://github.com/airbytehq/airbyte/pull/37131) | schema descriptions |
| 0.3.1 | 2023-11-21 | [32705](https://github.com/airbytehq/airbyte/pull/32705) | Update CDK version |
| 0.3.0 | 2023-11-14 | [23317](https://github.com/airbytehq/airbyte/pull/23317) | Update schemas |
| 0.2.1 | 2023-02-22 | [23317](https://github.com/airbytehq/airbyte/pull/23317) | Remove support for incremental for `order_statuses` stream |
| 0.2.0 | 2022-09-21 | [16612](https://github.com/airbytehq/airbyte/pull/16612) | Source Cart.com: implement Central API Router access method and improve backoff policy |
| 0.1.6 | 2022-07-15 | [14752](https://github.com/airbytehq/airbyte/pull/14752) | Add `order_statuses` stream |
| 0.1.5 | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.3 | 2021-08-26 | [5465](https://github.com/airbytehq/airbyte/pull/5465) | Add the end_date option for limitation of the amount of synced data |
| 0.1.2 | 2021-08-23 | [1111](https://github.com/airbytehq/airbyte/pull/1111) | Add `order_items` stream |
| 0.1.0 | 2021-06-08 | [4574](https://github.com/airbytehq/airbyte/pull/4574) | Initial Release |

</details>
