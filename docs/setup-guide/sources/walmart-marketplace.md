# Walmart Marketplace

This page contains the setup guide and reference information for Walmart Marketplace.

## Prerequisites

* Client ID
* Client Secret

## Setup guide

### Step 1: Get your Walmart API keys

1. Log in to your [Walmart seller dashboard](https://seller.walmart.com).

2. Click on **Settings** -> **API Key Management**.
![Walmart Settings](/docs/setup-guide/assets/images/walmart-settings.jpg "Walmart Settings")

3. Once you're on the API Integrations page, click **API Key Management**. You will be redirected to the Walmart developer portal.
![Walmart API Key Management](/docs/setup-guide/assets/images/walmart-api-key-mgnt.jpg "Walmart API Key Management")

4. Note down the **Client ID** and **Client secret** on the ***My API Key*** section under the ***Production keys*** tab. These will be used to create the integration in Daspire.
![Walmart API Key](/docs/setup-guide/assets/images/walmart-api-key.jpg "Walmart API Key")

### Step 2: Set up the Walmart data source in Daspire

1. Select **Walmart** from the Source list.

2. Enter a **Source Name**.

3. Enter your Walmart **Store Name**.

4. Enter your Walmart account **Client ID**.

5. Enter your Walmart account **Client Secret**.

6. In **Data Replication Schedule**, choose an option between **Based on Start Date** or **Periodic Replication**.

7. Click **Save & Test**.

## Supported sync modes

The Walmart data source supports the following sync modes:

* Full Refresh
* Incremental

## Supported streams

This source is capable of syncing the following streams:

* [Items](https://developer.walmart.com/api/us/mp/items#operation/getAllItems)
* [Orders](https://developer.walmart.com/api/us/mp/orders#operation/getAllOrders)
* [Returns](https://developer.walmart.com/api/us/mp/returns#operation/getReturns)
* [Multiple Item Inventory for All Ship Nodes](https://developer.walmart.com/api/us/mp/inventory#operation/getMultiNodeInventoryForAllSkuAndAllShipNodes)
* [WFS Inventory](https://developer.walmart.com/api/us/mp/inventory#operation/getWFSInventory)
* [Get Shipments](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipments)
* [Get Inbound Shipment Items](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipmentItems)
* [All Departments](https://developer.walmart.com/api/us/mp/utilities#operation/getDepartmentList)

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `int, float, number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |
