# WooCommerce

## Sync overview

The WooCommerce source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [WooCommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/).

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-customers)
* [Orders](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-orders)
* [Coupons](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-coupons)

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

1. Navigate to your store’s WordPress admin interface, go to (WooCommerce > Settings > Advanced > REST API)
2. Click on "Add Key" to generate an API Key
3. Choose the level of access for this REST API key, which can be Read access, Write access or Read/Write access. Airbyte only needs read-level access.
    * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
4. The two keys, Consumer Key and Consumer Secret are what you'll use respectively as `api_key` and `api_secret` for the integration.
5. You're ready to set up WooCommerce in Airbyte!


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.1.1  | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.0  | 2021-09-09 | [5955](https://github.com/airbytehq/airbyte/pull/5955) | Initial Release. Source WooCommerce |
