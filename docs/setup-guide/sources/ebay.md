# eBay

This page contains the setup guide and reference information for eBay.

## Prerequisites
* Client ID
* Client Secret
* Refresh Token

## Setup guide

### Step 1: Get your eBay API keys

1.  Log in to the eBay Developer Program and navigate to **Your Account > Application Keys**.

2. On the Application Keys page, get the **App ID (Client ID)**, **Cert ID (Client Secret)**, and **Refresh Token** values for the **Production environment**. These will be used to create the integration in Daspire.

### Step 2: Set up the eBay data source in Daspire

1. Select **eBay** from the Source list.

2. Enter a **Source Name**.

3. Enter your eBay **Store Name**.

4. Enter your eBay **Client Id**.

5. Enter your eBay **Client Secret**.

6. Enter your eBay **Refresh Token**.

7. In Acquisition Method, enter the  **Start Time**, which is used for generating reports starting from the specified start date. Should be in YYYY-MM-DD format and not more than 60 days in the past. The date for a specific profile is calculated according to its timezone. This parameter should be specified in the UTC timezone. Since it doesn't make sense to generate reports for the current day (metrics could be changed), it generates reports for the day before (e.g. if **Start Date** is 2022-10-11 it would use 20221010 as reportDate parameter for request).

8. Click **Set up source**.

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

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |