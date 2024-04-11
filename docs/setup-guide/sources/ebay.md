# eBay

This page contains the setup guide and reference information for eBay.

## Prerequisites
* eBay Store Name
* eBay Account Login (username and password)

## Setup guide

1. Select **eBay** from the Source list.

2. Enter a **Source Name**.

3. **Authenticate your eBay account**.

4. In **Data Replication Schedule**, choose an option between **Based on Start Date** or **Periodic Replication**.

5. Click **Save & Test**.

## Supported sync modes

The eBay data source supports the following sync modes:

* Full Refresh
* Incremental

## Supported streams

This source is capable of syncing the following streams:

* [Analytics](https://developer.ebay.com/api-docs/sell/analytics/resources/methods)
* [Payouts](https://developer.ebay.com/api-docs/sell/finances/resources/payout/methods/getPayouts)
* [Transactions](https://developer.ebay.com/api-docs/sell/finances/resources/transaction/methods/getTransactions)
* [Orders](https://developer.ebay.com/api-docs/sell/fulfillment/resources/order/methods/getOrders)
* [Inventory Items](https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/getInventoryItems)
* [Inventory Locations](https://developer.ebay.com/api-docs/sell/inventory/resources/location/methods/getInventoryLocations)
* [Campaigns](https://developer.ebay.com/api-docs/sell/marketing/resources/campaign/methods/getCampaigns)
* [Promotions](https://developer.ebay.com/api-docs/sell/marketing/resources/promotion/methods/getPromotions)
* [Promotion Reports](https://developer.ebay.com/api-docs/sell/marketing/resources/promotion_report/methods/getPromotionReports)

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |