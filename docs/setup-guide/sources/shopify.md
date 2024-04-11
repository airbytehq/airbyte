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

### Using API password to set up

1. Go to https://admin.shopify.com/store/YOURSTORE, click **Settings** from the side menu.
![Shopify Store Settings](/docs/setup-guide/assets/images/shopify-settings.jpg "Shopify Store Settings")

2. Click **Apps and sales channels** from the side menu. Then click **Develop apps**.
![Shopify Develop Apps](/docs/setup-guide/assets/images/shopify-develop-apps.jpg "Shopify Develop Apps")

3. Click **Create an app** to create a private application.
![Shopify Create an App](/docs/setup-guide/assets/images/shopify-create-app.jpg "Shopify Create an App")

4. Enter your **App name** and select the appropriate **App developer**.
![Shopify Create an App](/docs/setup-guide/assets/images/shopify-create-app2.jpg "Shopify Create an App")

5. Open the App you just created, click **Configuration**. Then click **Configure** in **Admin API integration**.
![Shopify Config](/docs/setup-guide/assets/images/shopify-configuration.jpg "Shopify Config")

6. In **Admin API access scopes**, select the resources you want to allow access to. Daspire only needs read-level access. Once you're done, click **Save**.

  > **Note:** The UI will show all possible data sources and will show errors when syncing if it doesn't have permissions to access a resource.
  
![Shopify Access Scopes](/docs/setup-guide/assets/images/shopify-access-scopes.jpg "Shopify Access Scopes")

7. Once you have assigned the APP relevant access scope, click the **API credentials** tab, and then click **Install app**. 
![Shopify API Credentials](/docs/setup-guide/assets/images/shopify-api-creds.jpg "Shopify API Credentials")

8. Once the app is installed, your **Admin API access token** will show, copy it. Your API access token starts with ***shpat_***. You'll use as the api\_password for the integration
![Shopify API Access Token](/docs/setup-guide/assets/images/shopify-api-access-token.jpg "Shopify API Access Token")

9. You're ready to set up Shopify in Daspire!

### Set up Shopify in Daspire

1. Select **Shopify** from the Source list.

2. Enter a **Source Name**.

3. Enter your Shopify **Store Name**.

4. Using OAuth 2.0, **Authenticate your Shopify account** or using API password, enter your **API password**.

5. Enter **Replication Start Date** - the date you would like to replicate data from. 

6. Click **Save & Test**.

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
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |
| `boolean` | `boolean` |

## Performance considerations

Shopify has some [rate limit restrictions](https://shopify.dev/concepts/about-apis/rate-limits). Typically, there should not be issues with throttling or exceeding the rate limits but in some edge cases, user can receive the warning message as follows:

```
Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

This is expected when the source hits the 429 - Rate Limit Exceeded HTTP Error. With the given error message, the sync operation still goes on, but will require more time to finish.

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.