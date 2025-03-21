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
| 0.3.15 | 2025-03-08 | [55402](https://github.com/airbytehq/airbyte/pull/55402) | Update dependencies |
| 0.3.14 | 2025-03-01 | [54851](https://github.com/airbytehq/airbyte/pull/54851) | Update dependencies |
| 0.3.13 | 2025-02-22 | [54245](https://github.com/airbytehq/airbyte/pull/54245) | Update dependencies |
| 0.3.12 | 2025-02-15 | [53887](https://github.com/airbytehq/airbyte/pull/53887) | Update dependencies |
| 0.3.11 | 2025-02-08 | [53416](https://github.com/airbytehq/airbyte/pull/53416) | Update dependencies |
| 0.3.10 | 2025-02-01 | [52925](https://github.com/airbytehq/airbyte/pull/52925) | Update dependencies |
| 0.3.9 | 2025-01-25 | [52203](https://github.com/airbytehq/airbyte/pull/52203) | Update dependencies |
| 0.3.8 | 2025-01-18 | [51724](https://github.com/airbytehq/airbyte/pull/51724) | Update dependencies |
| 0.3.7 | 2025-01-11 | [51224](https://github.com/airbytehq/airbyte/pull/51224) | Update dependencies |
| 0.3.6 | 2024-12-28 | [50464](https://github.com/airbytehq/airbyte/pull/50464) | Update dependencies |
| 0.3.5 | 2024-12-21 | [50194](https://github.com/airbytehq/airbyte/pull/50194) | Update dependencies |
| 0.3.4 | 2024-12-14 | [49568](https://github.com/airbytehq/airbyte/pull/49568) | Update dependencies |
| 0.3.3 | 2024-12-12 | [49312](https://github.com/airbytehq/airbyte/pull/49312) | Update dependencies |
| 0.3.2 | 2024-12-11 | [49016](https://github.com/airbytehq/airbyte/pull/49016) | Starting with this version, the Docker image is now rootless. Please note that this and future versions will not be compatible with Airbyte versions earlier than 0.64 |
| 0.3.1 | 2024-11-04 | [48234](https://github.com/airbytehq/airbyte/pull/48234) | Update dependencies |
| 0.3.0 | 2024-10-30 | [47277](https://github.com/airbytehq/airbyte/pull/47277) | Migrate to Manifest-only |
| 0.2.22 | 2024-10-28 | [47117](https://github.com/airbytehq/airbyte/pull/47117) | Update dependencies |
| 0.2.21 | 2024-10-12 | [46840](https://github.com/airbytehq/airbyte/pull/46840) | Update dependencies |
| 0.2.20 | 2024-10-05 | [46453](https://github.com/airbytehq/airbyte/pull/46453) | Update dependencies |
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
