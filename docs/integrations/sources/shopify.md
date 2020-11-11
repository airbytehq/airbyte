# Shopify

## Sync overview

This source can sync data for the [Shopify API](https://help.shopify.com/en/api/reference).

This Source Connector is based on a [Singer Tap](https://github.com/singer-io/tap-shopify).

### Output schema

This Source is capable of syncing the following core Streams:

* [Abandoned Checkouts](https://help.shopify.com/en/api/reference/orders/abandoned_checkouts)
* [Collects](https://help.shopify.com/en/api/reference/products/collect)
* [Custom Collections](https://help.shopify.com/en/api/reference/products/customcollection)
* [Customers](https://help.shopify.com/en/api/reference/customers)
* [Metafields](https://help.shopify.com/en/api/reference/metafield)
* [Orders](https://help.shopify.com/en/api/reference/orders)
* [Products](https://help.shopify.com/en/api/reference/products)
* [Transactions](https://help.shopify.com/en/api/reference/orders/transaction)

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
| Full Refresh Sync | yes |  |
| Incremental Sync | no |  |

### Performance considerations

Shopify has some [rate limit restrictions](https://shopify.dev/concepts/about-apis/rate-limits).

## Getting started

1. Go to `https://YOURSTORE.myshopify.com/admin/apps/private`
1. Enable private development if it isn't enabled.
1. Create a private application.
1. Select the resources you want to allow access to. Airbyte only needs read-level access. 
   * Note: The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource. 
1. The password under the `Admin API` section is what you'll use as the `api_password` for the integration.
1. You're ready to set up Shopify in Airbyte!
