## Prerequisites

* An Active [Shopify store](https://www.shopify.com)

::: note

If you are already a Cloud user but still use the `API PASSWORD` authentication method (option), please make sure you've switched to the `OAuth2.0`, as far as the `API PASSWORD` is going to be deprecated soon for Cloud Users, but this option remains for `OSS` users.

:::

## Setup guide

### Connect using OAuth2.0
1. Click `Authenticate your Shopify account` to start the autentication.
2. Click `Install` to install Airbyte application.
3. Log in to your account, if not already.
4. Select the store you want to sync and review the consent.
5. Click on `Install` to finish the Installation.
6. Reveiew the `Shop Name` field for the chosen store for a sync.
7. Set the `Start Date` as the starting point for your data replication.
8. Click `Test and Save` to finish the source set up.

You're ready to set up Shopify in Airbyte!

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