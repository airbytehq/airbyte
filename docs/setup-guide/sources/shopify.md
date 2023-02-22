# Shopify

This page contains the setup guide and reference information for Shopify.

## Prerequisites

* Your Shopify store name
* Your Shopify login details or API password

## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes |
| Namespaces | No |

The Shopify source supports both **Full Refresh** and **Incremental** syncs. You can choose to copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

Daspire can sync data for the [Shopify API](https://help.shopify.com/en/api/reference).

## Setup guide

This source supports API PASSWORD authentication method.

1. Go to https://YOURSTORE.myshopify.com/admin/apps/private

2. Enable private development if it isn't enabled.

3. Create a private application.

4. Select the resources you want to allow access to. Daspire only needs read-level access.

  > **Note:** The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.

5. The password under the Admin API section is what you'll use as the api\_password for the integration.

6. You're ready to set up Shopify in Daspire!

## Output schema

This Source is capable of syncing the following core Streams:

* [Abandoned Checkouts](https://help.shopify.com/en/api/reference/orders/abandoned_checkouts)
* [Collects](https://help.shopify.com/en/api/reference/products/collect)
* [Custom Collections](https://help.shopify.com/en/api/reference/products/customcollection)
* [Customers](https://help.shopify.com/en/api/reference/customers)
* [Draft Orders](https://help.shopify.com/en/api/reference/orders/draftorder)
* [Discount Codes](https://shopify.dev/docs/admin-api/rest/reference/discounts/discountcode)
* [Metafields](https://help.shopify.com/en/api/reference/metafield)
* [Orders](https://help.shopify.com/en/api/reference/order)
* [Orders Refunds](https://shopify.dev/api/admin/rest/reference/orders/refund)
* [Orders Risks](https://shopify.dev/api/admin/rest/reference/orders/order-risk)
* [Products](https://help.shopify.com/en/api/reference/products)
* [Transactions](https://help.shopify.com/en/api/reference/orders/transaction)
* [Balance Transactions](https://shopify.dev/api/admin-rest/2021-07/resources/transactions)
* [Pages](https://help.shopify.com/en/api/reference/online-store/page)
* [Price Rules](https://help.shopify.com/en/api/reference/discounts/pricerule)
* [Locations](https://shopify.dev/api/admin-rest/2021-10/resources/location)
* [InventoryItems](https://shopify.dev/api/admin-rest/2021-10/resources/inventoryItem)
* [InventoryLevels](https://shopify.dev/api/admin-rest/2021-10/resources/inventorylevel)
* [Fulfillment Orders](https://shopify.dev/api/admin-rest/2021-07/resources/fulfillmentorder)
* [Fulfillments](https://shopify.dev/api/admin-rest/2021-07/resources/fulfillment)
* [Shop](https://shopify.dev/api/admin-rest/2021-07/resources/shop)

**NOTE**

For better experience with Incremental Refresh the following is recommended:

1. Order Refunds, Order Risks, Transactions should be synced along with Orders stream.

2. Discount Codes should be synced along with Price Rules stream.

If child streams are synced alone from the parent stream - the full sync will take place, and the records are filtered out afterwards.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| string | string |
| number | number |
| array | array |
| object | object |
| boolean | boolean |

## Performance considerations

Shopify has some [rate limit restrictions](https://shopify.dev/concepts/about-apis/rate-limits). Typically, there should not be issues with throttling or exceeding the rate limits but in some edge cases, user can receive the warning message as follows:

```
Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the source hits the 429 - Rate Limit Exceeded HTTP Error. With the given error message, the sync operation still goes on, but will require more time to finish.