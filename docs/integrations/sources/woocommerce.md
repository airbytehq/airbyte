# Woocommerce

## Sync overview

The Woocommerce source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [Woocommerce API](http://woocommerce.github.io/woocommerce-rest-api-docs).

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/contributing-to-airbyte/python).

### Output schema

This Source is capable of syncing the following core Streams:

* [Abandoned Checkouts](https://help.shopify.com/en/api/reference/orders/abandoned_checkouts)
* [Collects](https://help.shopify.com/en/api/reference/products/collect)
* [Custom Collections](https://help.shopify.com/en/api/reference/products/customcollection)
* [Customers](https://help.shopify.com/en/api/reference/customers)
* [Draft Orders](https://help.shopify.com/en/api/reference/orders/draftorder)
* [Discount Codes](https://shopify.dev/docs/admin-api/rest/reference/discounts/discountcode)
* [Metafields](https://help.shopify.com/en/api/reference/metafield)
* [Orders](https://help.shopify.com/en/api/reference/orders)
* [Products](https://help.shopify.com/en/api/reference/products)
* [Transactions](https://help.shopify.com/en/api/reference/orders/transaction)
* [Pages](https://help.shopify.com/en/api/reference/online-store/page)
* [Price Rules](https://help.shopify.com/en/api/reference/discounts/pricerule)

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
| Incremental - Append Sync | Yes |  |
| Namespaces | No |  |

## Getting started

1. Log into your Woocommerce admin page at `https://YOURSTORELINK.com/admin`
2. Generate API Keys in the WordPress Admin interface by going to go to WooCommerce > Settings > Advanced > REST API.
   Click the "Add Key" button. In the next screen, add a description and select the WordPress user you would like to generate the key for.
   * Note: Keys/Apps was found at WooCommerce > Settings > API > Key/Apps prior to WooCommerce 3.4.
3. Choose the level of access for this REST API key, which can be Read access, Write access or Read/Write access. Then click the "Generate API Key" button and WooCommerce will generate REST API keys for the selected user.
    * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
5. These two keys are your Consumer Key and Consumer Secret which respectively represent `Api key` and `Api secret` required for the integration
6. You're ready to set up Woocommerce in Airbyte!


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.0   | 2021-07-30 | [3787](https://github.com/airbytehq/airbyte/pull/3787) | Add woocommerce Source Connector |
