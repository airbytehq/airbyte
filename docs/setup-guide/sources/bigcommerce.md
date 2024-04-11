# BigCommerce

This page contains the setup guide and reference information for BigCommerce.

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

## Prerequisites

* BigCommerce [high-risk user permission](https://support.bigcommerce.com/s/article/User-Permissions?language=en_US#highrisk)

## Setup guide

1. Navigate to your store's control panel. In the left side menu, click **Settings**. On the page opened on the right side, scroll down and find **Store-level API accounts**.
![BigCommerce API Accounts](/docs/setup-guide/assets/images/bigcommerce-settings.jpg "BigCommerce API Accounts")

2. Click **Create an API account**.
![BigCommerce Create API Accounts](/docs/setup-guide/assets/images/bigcommerce-create-api-account.jpg "BigCommerce Create API Accounts")

3. Select the resources you want to allow access to. Daspire only needs read-level access.
![BigCommerce API Scope](/docs/setup-guide/assets/images/bigcommerce-api-scope.jpg "BigCommerce API Scope")

4. Once you're done with the selection, click **Save**. You will get **Client ID**, **Client secret**, and **Access token**. Copy them, you will use them later to set up the source.
![BigCommerce API Credentials](/docs/setup-guide/assets/images/bigcommerce-creds.jpg "BigCommerce API Credentials")

5. You're ready to set up BigCommerce in Daspire!

## Sync overview

The BigCommerce source supports both **Full Refresh** and **Incremental** syncs. You can choose to copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Daspire can sync data for the [BigCommerce API](https://developer.bigcommerce.com/api-docs/getting-started/making-requests).

## Output schema

This Source is capable of syncing the following core Streams:

* [Customers](https://developer.bigcommerce.com/api-reference/store-management/customers-v3/customers/customersget)
* [Orders](https://developer.bigcommerce.com/api-reference/store-management/orders/orders/getallorders)
* [Transactions](https://developer.bigcommerce.com/docs/rest-management/transactions#get-transactions)
* [Pages](https://developer.bigcommerce.com/api-reference/store-management/store-content/pages/getallpages)
* [Products](https://developer.bigcommerce.com/api-reference/store-management/catalog/products/getproducts)
* [Channels](https://developer.bigcommerce.com/api-reference/d2298071793d6-get-all-channels)
* [Store](https://developer.bigcommerce.com/docs/rest-management/store-information#get-store-information)
* [OrderProducts](https://developer.bigcommerce.com/api-reference/3b4dfef625708-list-order-products)
* [Brands](https://developer.bigcommerce.com/api-reference/c2610608c20c8-get-all-brands)
* [Categories](https://developer.bigcommerce.com/api-reference/9cc3a53863922-get-all-categories)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## Performance considerations

BigCommerce has some [rate limit restrictions](https://developer.bigcommerce.com/api-docs/getting-started/best-practices).

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.
