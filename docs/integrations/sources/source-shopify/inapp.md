## Prerequisites

* An Active [Shopify store](https://www.shopify.com) 
* The Admin API access token of your [Custom App](https://help.shopify.com/en/manual/apps/app-types/custom-apps).

:::note

Our Shopify Source Connector does not support OAuth at this time due to limitations outside of our control. If OAuth for Shopify is critical to your business, [please reach out to us](mailto:product@airbyte.io) to discuss how we may be able to partner on this effort.
 
:::

## Setup guide

1. Name your source.
2. Enter your Store name. You can find this in your URL when logged in to Shopify or within the Store details section of your Settings.
3. Enter your Admin API access token. To set up the access token, you will need to set up a custom application. See instructions below on creating a custom app.
4. Click Set up source

## Creating a Custom App
Authentication to the Shopify API requies a [custom application](https://help.shopify.com/en/manual/apps/app-types/custom-apps). Follow these instructions to create a custom app and find your Admin API Access Token.

1. Navigate to Settings > App and sales channels > Develop apps > Create an app
2. Name your new app
3. Select **Configure Admin API scopes**
4. Tick all the scopes prefixed with `read_` (e.g. `read_locations`,`read_price_rules`, etc ) and save. See below for the full list of scopes to allow.
5. Click **Install app** to give this app access to your data. 
6. Once installed, go to **API Credentials** to copy the **Admin API Access Token**. 

### Scopes Required for Custom App
Add the following scopes to your custom app to ensure Airbyte can sync all available data. To see a list of streams this source supports, see our full [Shopify documentation](https://docs.airbyte.com/integrations/sources/shopify/).
* `read_analytics`
* `read_assigned_fulfillment_orders`
* `read_gdpr_data_request`
* `read_locations`
* `read_price_rules` 
* `read_product_listings` 
* `read_products` 
* `read_reports` 
* `read_resource_feedbacks` 
* `read_script_tags` 
* `read_shipping`
* `read_locales`
* `read_shopify_payments_accounts` 
* `read_shopify_payments_bank_accounts` 
* `read_shopify_payments_disputes`
* `read_shopify_payments_payouts`
* `read_content`
* `read_themes`
* `read_third_party_fulfillment_orders`
* `read_translations`
* `read_customers`
* `read_discounts` 
* `read_draft_orders` 
* `read_fulfillments` 
* `read_gift_cards`
* `read_inventory`
* `read_legal_policies` 
* `read_marketing_events` 
* `read_merchant_managed_fulfillment_orders` 
* `read_online_store_pages`
* `read_order_edits`
* `read_orders`

​
For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Shopify](https://docs.airbyte.com/integrations/sources/shopify).