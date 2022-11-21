# BigCommerce

This page contains the setup guide and reference information for BigCommerce.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

## Setup guide

1. Navigate to your store's control panel (Advanced Settings \> API Accounts \> Create API Account)

2. Create an API account.

3. Select the resources you want to allow access to. Daspire only needs read-level access.

  > **Note:** The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.

4. The generated Access Token is what you'll use as the access\_token for the integration.

5. You're ready to set up BigCommerce in Daspire!

## Sync overview

The BigCommerce source supports both **Full Refresh** and **Incremental** syncs. You can choose to copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Daspire can sync data for the [BigCommerce API](https://developer.bigcommerce.com/api-docs/getting-started/making-requests).

## Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://developer.bigcommerce.com/api-reference/store-management/customers-v3/customers/customersget)
* [Orders](https://developer.bigcommerce.com/api-reference/store-management/orders/orders/getallorders)
* [Transactions](https://developer.bigcommerce.com/api-reference/store-management/order-transactions/transactions/gettransactions)
* [Pages](https://developer.bigcommerce.com/api-reference/store-management/store-content/pages/getallpages)
* [Products](https://developer.bigcommerce.com/api-reference/store-management/catalog/products/getproducts)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| string | string |
| number | number |
| array | array |
| object | object |

## Performance considerations

BigCommerce has some [rate limit restrictions](https://developer.bigcommerce.com/api-docs/getting-started/best-practices).