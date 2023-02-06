# BigCommerce

## Sync overview

The BigCommerce source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [BigCommerce API](https://developer.bigcommerce.com/api-docs/getting-started/making-requests).

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This Source is capable of syncing the following core Streams:

- [Customers](https://developer.bigcommerce.com/api-reference/store-management/customers-v3/customers/customersget)
- [Orders](https://developer.bigcommerce.com/api-reference/store-management/orders/orders/getallorders)
- [Transactions](https://developer.bigcommerce.com/api-reference/store-management/order-transactions/transactions/gettransactions)
- [Pages](https://developer.bigcommerce.com/api-reference/store-management/store-content/pages/getallpages)
- [Products](https://developer.bigcommerce.com/api-reference/store-management/catalog/products/getproducts)
- [Channels](https://developer.bigcommerce.com/api-reference/d2298071793d6-get-all-channels)
- [Store](https://developer.bigcommerce.com/api-reference/bb1daaaeccae0-get-store-information)
- [OrderProducts](https://developer.bigcommerce.com/api-reference/3b4dfef625708-list-order-products)
- [Brands](https://developer.bigcommerce.com/api-reference/c2610608c20c8-get-all-brands)
- [Categories](https://developer.bigcommerce.com/api-reference/9cc3a53863922-get-all-categories)

### Data type mapping

| Integration Type | Airbyte Type | Notes |
| :--------------- | :----------- | :---- |
| `string`         | `string`     |       |
| `number`         | `number`     |       |
| `array`          | `array`      |       |
| `object`         | `object`     |       |

### Features

| Feature                   | Supported?\(Yes/No\) | Notes |
| :------------------------ | :------------------- | :---- |
| Full Refresh Sync         | Yes                  |       |
| Incremental - Append Sync | Yes                  |       |
| Namespaces                | No                   |       |

### Performance considerations

BigCommerce has some [rate limit restrictions](https://developer.bigcommerce.com/api-docs/getting-started/best-practices).

## Getting started

1. Navigate to your store’s control panel \(Advanced Settings &gt; API Accounts &gt; Create API Account\)
2. Create an API account.
3. Select the resources you want to allow access to. Airbyte only needs read-level access.
   - Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
4. The generated `Access Token` is what you'll use as the `access_token` for the integration.
5. You're ready to set up BigCommerce in Airbyte!

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                     |
|:--------|:-----------|:---------------------------------------------------------|:------------------------------------------------------------|
| 0.1.10  | 2022-12-16 | [20518](https://github.com/airbytehq/airbyte/pull/20518) | Add brands and categories streams                           |
| 0.1.9   | 2022-12-15 | [20540](https://github.com/airbytehq/airbyte/pull/20540) | Rebuild on CDK 0.15.0                                       |
| 0.1.8   | 2022-12-15 | [20090](https://github.com/airbytehq/airbyte/pull/20090) | Add order_products stream                                   |
| 0.1.7   | 2022-09-13 | [16647](https://github.com/airbytehq/airbyte/pull/16647) | Add channel and store stream goes beyond                    |
| 0.1.6   | 2022-07-27 | [14940](https://github.com/airbytehq/airbyte/pull/14940) | Fix infinite loop when the page stream goes beyond one page |
| 0.1.5   | 2022-01-31 | [9935](https://github.com/airbytehq/airbyte/pull/9935)   | Correct date-time columns for `orders` (v2 stream)          |
| 0.1.4   | 2022-01-13 | [9516](https://github.com/airbytehq/airbyte/pull/9516)   | Add Catalog Products Stream and fix date-time parsing       |
| 0.1.3   | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434)   | Update fields in source-connectors specifications           |
| 0.1.2   | 2021-12-07 | [8416](https://github.com/airbytehq/airbyte/pull/8416)   | Correct Incremental Function                                |
| 0.1.1   | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499)   | Remove base-python dependencies                             |
| 0.1.0   | 2021-08-19 | [5521](https://github.com/airbytehq/airbyte/pull/5521)   | Initial Release. Source BigCommerce                         |
