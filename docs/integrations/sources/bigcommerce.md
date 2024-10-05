# BigCommerce

## Sync overview

The BigCommerce source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [BigCommerce API](https://developer.bigcommerce.com/api-docs/getting-started/making-requests).

### Output schema

This Source is capable of syncing the following core Streams:

- [Customers](https://developer.bigcommerce.com/api-reference/store-management/customers-v3/customers/customersget)
- [Orders](https://developer.bigcommerce.com/api-reference/store-management/orders/orders/getallorders)
- [Transactions](https://developer.bigcommerce.com/docs/rest-management/transactions#get-transactions)
- [Pages](https://developer.bigcommerce.com/api-reference/store-management/store-content/pages/getallpages)
- [Products](https://developer.bigcommerce.com/api-reference/store-management/catalog/products/getproducts)
- [Channels](https://developer.bigcommerce.com/api-reference/d2298071793d6-get-all-channels)
- [Store](https://developer.bigcommerce.com/docs/rest-management/store-information#get-store-information)
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

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                     |
| :------ | :--------- | :------------------------------------------------------- | :---------------------------------------------------------- |
| 0.2.19 | 2024-09-28 | [46206](https://github.com/airbytehq/airbyte/pull/46206) | Update dependencies |
| 0.2.18 | 2024-09-21 | [45725](https://github.com/airbytehq/airbyte/pull/45725) | Update dependencies |
| 0.2.17 | 2024-09-14 | [45539](https://github.com/airbytehq/airbyte/pull/45539) | Update dependencies |
| 0.2.16 | 2024-09-07 | [45292](https://github.com/airbytehq/airbyte/pull/45292) | Update dependencies |
| 0.2.15 | 2024-08-31 | [44979](https://github.com/airbytehq/airbyte/pull/44979) | Update dependencies |
| 0.2.14 | 2024-08-24 | [44693](https://github.com/airbytehq/airbyte/pull/44693) | Update dependencies |
| 0.2.13 | 2024-08-17 | [43827](https://github.com/airbytehq/airbyte/pull/43827) | Update dependencies |
| 0.2.12 | 2024-08-10 | [43630](https://github.com/airbytehq/airbyte/pull/43630) | Update dependencies |
| 0.2.11 | 2024-08-03 | [43124](https://github.com/airbytehq/airbyte/pull/43124) | Update dependencies |
| 0.2.10 | 2024-07-27 | [42773](https://github.com/airbytehq/airbyte/pull/42773) | Update dependencies |
| 0.2.9 | 2024-07-20 | [42192](https://github.com/airbytehq/airbyte/pull/42192) | Update dependencies |
| 0.2.8 | 2024-07-13 | [41883](https://github.com/airbytehq/airbyte/pull/41883) | Update dependencies |
| 0.2.7 | 2024-07-10 | [41540](https://github.com/airbytehq/airbyte/pull/41540) | Update dependencies |
| 0.2.6 | 2024-07-09 | [41256](https://github.com/airbytehq/airbyte/pull/41256) | Update dependencies |
| 0.2.5 | 2024-07-06 | [40997](https://github.com/airbytehq/airbyte/pull/40997) | Update dependencies |
| 0.2.4 | 2024-06-25 | [40334](https://github.com/airbytehq/airbyte/pull/40334) | Update dependencies |
| 0.2.3 | 2024-06-22 | [40113](https://github.com/airbytehq/airbyte/pull/40113) | Update dependencies |
| 0.2.2 | 2024-06-06 | [39251](https://github.com/airbytehq/airbyte/pull/39251) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.1 | 2024-05-21 | [38528](https://github.com/airbytehq/airbyte/pull/38528) | [autopull] base image + poetry + up_to_date |
| 0.2.0 | 2023-08-16 | [29469](https://github.com/airbytehq/airbyte/pull/29469) | Migrate Python CDK to Low Code |
| 0.1.10 | 2022-12-16 | [20518](https://github.com/airbytehq/airbyte/pull/20518) | Add brands and categories streams |
| 0.1.9 | 2022-12-15 | [20540](https://github.com/airbytehq/airbyte/pull/20540) | Rebuild on CDK 0.15.0 |
| 0.1.8 | 2022-12-15 | [20090](https://github.com/airbytehq/airbyte/pull/20090) | Add order_products stream |
| 0.1.7 | 2022-09-13 | [16647](https://github.com/airbytehq/airbyte/pull/16647) | Add channel and store stream goes beyond |
| 0.1.6 | 2022-07-27 | [14940](https://github.com/airbytehq/airbyte/pull/14940) | Fix infinite loop when the page stream goes beyond one page |
| 0.1.5 | 2022-01-31 | [9935](https://github.com/airbytehq/airbyte/pull/9935) | Correct date-time columns for `orders` (v2 stream) |
| 0.1.4 | 2022-01-13 | [9516](https://github.com/airbytehq/airbyte/pull/9516) | Add Catalog Products Stream and fix date-time parsing |
| 0.1.3 | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.2 | 2021-12-07 | [8416](https://github.com/airbytehq/airbyte/pull/8416) | Correct Incremental Function |
| 0.1.1 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.0 | 2021-08-19 | [5521](https://github.com/airbytehq/airbyte/pull/5521) | Initial Release. Source BigCommerce |

</details>
