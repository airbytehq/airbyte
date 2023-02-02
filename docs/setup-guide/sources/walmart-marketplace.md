# Walmart

This page contains the setup guide and reference information for Walmart.

## Prerequisites
* Client ID
* Client Secret

## Setup guide

### Step 1: Get your Walmart API keys

1. Log in to your [Walmart seller dashboard](https://seller.walmart.com).

2. Click on **Settings** -> **API Key Management**  

3. Click on **Walmart Developer Portal**. You will be redirected to the Walmart developer portal.

4. Note down the **Client ID** and **Client secret** on **Production keys** tab. These will be used to create the integration in Daspire.

### Step 2: Set up the Walmart data source in Daspire

1. Select **Walmart** from the Source list.

2. Enter a **Source Name**.

3. Enter your Walmart **Store Name**.

4. Enter your Walmart account **Client ID**.

5. Enter your Walmart account **Client Secret**.

6. In Acquisition Method, enter the  **Start Time**, which is used for generating reports starting from the specified start date. Should be in YYYY-MM-DD format and not more than 60 days in the past. The date for a specific profile is calculated according to its timezone, this parameter should be specified in the UTC timezone. Since it doesn't make sense to generate reports for the current day (metrics could be changed), it generates reports for the day before (e.g. if **Start Date** is 2022-10-11 it would use 20221010 as reportDate parameter for request).

7. Click **Set up source**.

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
* [Items Reports](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [Buybox Reports](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [CPA Reports](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [Item Performance Reports](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [Return Overrides Reports](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [Promp Reports](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [Get Shipments](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipments)
* [Get Inbound Shipment Items](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipmentItems)
* [All Departments](https://developer.walmart.com/api/us/mp/utilities#operation/getDepartmentList)

## Data type mapping

| Integration Type | Daspire Type |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |