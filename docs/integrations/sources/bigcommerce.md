# BigCommerce

## Sync overview

The BigCommerce source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source can sync data for the [BigCommerce API](https://developer.bigcommerce.com/api-docs/getting-started/making-requests).

This Source Connector is based on a [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

### Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://developer.bigcommerce.com/api-reference/store-management/customers-v3/customers/customersget)
* [Orders](https://developer.bigcommerce.com/api-reference/store-management/orders/orders/getallorders)
* [Transactions](https://developer.bigcommerce.com/api-reference/store-management/order-transactions/transactions/gettransactions)
* [Pages](https://developer.bigcommerce.com/api-reference/store-management/store-content/pages/getallpages)

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

### Performance considerations

BigCommerce has some [rate limit restrictions](https://developer.bigcommerce.com/api-docs/getting-started/best-practices).

## Getting started

1. Navigate to your store’s control panel \(Advanced Settings &gt; API Accounts &gt; Create API Account\)
2. Create an API account.
3. Select the resources you want to allow access to. Airbyte only needs read-level access.
   * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
4. The generated `Access Token` is what you'll use as the `access_token` for the integration. 
5. You're ready to set up BigCommerce in Airbyte!

## Changelog

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.3 | 2021-12-23 | [8434](https://github.com/airbytehq/airbyte/pull/8434) | Update fields in source-connectors specifications |
| 0.1.2 | 2021-12-07 | [8416](https://github.com/airbytehq/airbyte/pull/8416) | Correct Incremental Function |
| 0.1.1 | 2021-11-08 | [7499](https://github.com/airbytehq/airbyte/pull/7499) | Remove base-python dependencies |
| 0.1.0 | 2021-08-19 | [5521](https://github.com/airbytehq/airbyte/pull/5521) | Initial Release. Source BigCommerce |

