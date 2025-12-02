# Cart.com

## Sync overview

This source can sync data for the [Cart.com API](https://developers.cart.com/docs/rest-api/docs/README.md). It supports both Full Refresh and Incremental sync for all streams. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

### Output schema

This Source is capable of syncing the following core Streams:

- [Addresses](https://developers.cart.com/docs/rest-api/b3A6MjMzMTc3Njc-get-addresses) (Incremental)
- [CustomersCart](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1customers/get) (Incremental)
- [OrderItems](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_items/get) (Incremental)
- [OrderPayments](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1order_payments/get) (Incremental)
- [Orders](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1orders/get) (Incremental)
- [OrderStatuses](https://developers.cart.com/docs/rest-api/ff5ada86bc8a0-get-order-statuses) (Full Refresh)
- [Products](https://developers.cart.com/docs/rest-api/restapi.json/paths/~1products/get) (Incremental)

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

- Cart.com account (formerly AmeriCommerce)
- Admin access to your Cart.com store
- Authentication credentials (either Single Store Access Token or Central API Router credentials)

### Setup guide

Cart.com supports two authentication methods. Choose the method that best fits your use case:

#### Single Store Access Token

This method is recommended for most users who need to sync data from a single Cart.com store.

1. Log in to your Cart.com admin console
2. Navigate to **Tools** > **Apps & Addons** > **API Apps & Integrations**
3. Find or create your API application
4. Click the **Tokens** icon (second icon from the left) next to your application
5. Click **New** to create a new access token
6. Select the required scopes for your integration
7. Click **Save**
8. Copy the access token from the token details view

When configuring the connector in Airbyte, you'll need:

- **Access Token**: The token you generated
- **Store Name**: Your store's domain name (for example, `mystorename.com`)

#### Central API Router

This method is designed for applications that need to access multiple Cart.com stores or require programmatic authentication.

1. Contact Cart.com support to set up Central API Router access
2. Obtain your provisioning credentials:
   - **User Name**: Your provisioning user name
   - **User Secret**: Your provisioning user secret
   - **Site ID**: Your site identifier

When configuring the connector in Airbyte, select the Central API Router authentication method and provide these credentials.

For more details on authentication, see the [Cart.com authentication documentation](https://developers.cart.com/docs/rest-api/ZG9jOjU4NjM4-cart-com-online-store-api-authentication).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                                |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| 0.3.38 | 2025-12-02 | [70284](https://github.com/airbytehq/airbyte/pull/70284) | Update dependencies |
| 0.3.37 | 2025-11-25 | [68900](https://github.com/airbytehq/airbyte/pull/68900) | Update dependencies |
| 0.3.36 | 2025-11-24 | [69783](https://github.com/airbytehq/airbyte/pull/69783) | Upgrade to Python 3.13, base image 4.1.0, and CDK 7.x |
| 0.3.35 | 2025-10-14 | [68085](https://github.com/airbytehq/airbyte/pull/68085) | Update dependencies |
| 0.3.34 | 2025-10-07 | [67194](https://github.com/airbytehq/airbyte/pull/67194) | Update dependencies |
| 0.3.33 | 2025-09-30 | [65341](https://github.com/airbytehq/airbyte/pull/65341) | Update dependencies |
| 0.3.32 | 2025-08-16 | [65042](https://github.com/airbytehq/airbyte/pull/65042) | Update dependencies |
| 0.3.31 | 2025-08-09 | [64653](https://github.com/airbytehq/airbyte/pull/64653) | Update dependencies |
| 0.3.30 | 2025-07-26 | [63783](https://github.com/airbytehq/airbyte/pull/63783) | Update dependencies |
| 0.3.29 | 2025-06-21 | [61884](https://github.com/airbytehq/airbyte/pull/61884) | Update dependencies |
| 0.3.28 | 2025-06-15 | [60717](https://github.com/airbytehq/airbyte/pull/60717) | Update dependencies |
| 0.3.27 | 2025-05-10 | [59773](https://github.com/airbytehq/airbyte/pull/59773) | Update dependencies |
| 0.3.26 | 2025-05-03 | [59323](https://github.com/airbytehq/airbyte/pull/59323) | Update dependencies |
| 0.3.25 | 2025-04-26 | [58740](https://github.com/airbytehq/airbyte/pull/58740) | Update dependencies |
| 0.3.24 | 2025-04-19 | [58262](https://github.com/airbytehq/airbyte/pull/58262) | Update dependencies |
| 0.3.23 | 2025-04-12 | [57614](https://github.com/airbytehq/airbyte/pull/57614) | Update dependencies |
| 0.3.22 | 2025-04-05 | [57124](https://github.com/airbytehq/airbyte/pull/57124) | Update dependencies |
| 0.3.21 | 2025-03-29 | [56592](https://github.com/airbytehq/airbyte/pull/56592) | Update dependencies |
| 0.3.20 | 2025-03-22 | [56133](https://github.com/airbytehq/airbyte/pull/56133) | Update dependencies |
| 0.3.19 | 2025-03-08 | [55408](https://github.com/airbytehq/airbyte/pull/55408) | Update dependencies |
| 0.3.18 | 2025-03-01 | [54879](https://github.com/airbytehq/airbyte/pull/54879) | Update dependencies |
| 0.3.17 | 2025-02-22 | [54281](https://github.com/airbytehq/airbyte/pull/54281) | Update dependencies |
| 0.3.16 | 2025-02-15 | [53886](https://github.com/airbytehq/airbyte/pull/53886) | Update dependencies |
| 0.3.15 | 2025-02-01 | [52906](https://github.com/airbytehq/airbyte/pull/52906) | Update dependencies |
| 0.3.14 | 2025-01-25 | [52205](https://github.com/airbytehq/airbyte/pull/52205) | Update dependencies |
| 0.3.13 | 2025-01-18 | [51751](https://github.com/airbytehq/airbyte/pull/51751) | Update dependencies |
| 0.3.12 | 2025-01-11 | [51294](https://github.com/airbytehq/airbyte/pull/51294) | Update dependencies |
| 0.3.11 | 2024-12-28 | [50505](https://github.com/airbytehq/airbyte/pull/50505) | Update dependencies |
| 0.3.10 | 2024-12-21 | [50189](https://github.com/airbytehq/airbyte/pull/50189) | Update dependencies |
| 0.3.9 | 2024-12-14 | [49316](https://github.com/airbytehq/airbyte/pull/49316) | Update dependencies |
| 0.3.8 | 2024-11-25 | [48637](https://github.com/airbytehq/airbyte/pull/48637) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.7 | 2024-11-04 | [43726](https://github.com/airbytehq/airbyte/pull/43726) | Update dependencies |
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
