# Rakuten-RMS

This source can sync data for the Rakuten RMS API.
The Rakuten RMS API reference is only available to subscribers.
This page guides you through the process of setting up the Rakuten RMS source connector.

## Prerequisites

- A Rakuten RMS account with permission to access data from accounts you want to sync.
- Rakuten RMS Service secret and Licence key 

## Step guide

### Step 1: Set up Rakuten RMS

Generate Service Secret and Licence key on the dashboard

### Step 2: Set up the source connector in Airbyte

<!-- env:oss -->

**For Airbyte Open Source:**

1. In the navigation bar, click Sources.
2. Click **New source**.
3. On the source setup page, select **Rakuten-RMS** from the Source type dropdown and enter a name for this connector;
4. Enter `Licence Key`;
5. Enter `Service Secret`;
6. (Optional) min_inventories
7. (Optional) max_inventories
8. (Optional) step_interval
7. click `Set up source`.
<!-- /env:oss -->

## Supported sync modes

The Rakuten RMS source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

| Feature           | Supported? |
| :---------------- | :--------- |
| Full Refresh Sync | Yes        |
| Incremental Sync  | Yes        |
| Namespaces        | No         |

## Supported Streams

Several output streams are available from this source

- inventories
- items
- items_sku_report
- purchase_order
- purchase_order_package_model
- genres
- genres_children
- category_mapping
- category_set_lists
- category_relation_report
- bundles
- version