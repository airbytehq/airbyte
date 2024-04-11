# Newegg

This page contains the setup guide and reference information for Newegg.

## Prerequisites


## Features

| Feature | Supported? |
| --- | --- |
| Full Refresh Sync | Yes |
| SSL connection | Yes |
| Namespaces | No |

## Setup guide

### Step 1: Obtain Newegg setup details

1. Login to your Newegg account.

2. 

5. You're ready to set up ShipStation in Daspire!

### Step 2: Set up Newegg in Daspire

1. Select **Newegg** from the Source list.

2. Enter a **Source Name**.

3. Enter your Newegg 

4. Enter your Newegg 

5. In **Data Replication Schedule**, choose an option between **Based on Start Date** or **Periodic Replication**.

6. Click **Save & Test**.

## Supported streams

This source is capable of syncing the following streams:

[Get Item Inventory](https://developer.newegg.com/newegg_marketplace_api/item_management/get_inventory/)
[Get Batch Inventory](https://developer.newegg.com/newegg_marketplace_api/item_management/get-batch-inventory/)
[Get Item Price](https://developer.newegg.com/newegg_marketplace_api/item_management/get_price/)
[Get Batch Price](https://developer.newegg.com/newegg_marketplace_api/item_management/get-batch-price/)
[Get Order Information](https://developer.newegg.com/newegg_marketplace_api/order_management/get_order_information/)
[Get Additional Order Information](https://developer.newegg.com/newegg_marketplace_api/order_management/get_additional_order_information/)
[Get RMA Information](https://developer.newegg.com/newegg_marketplace_api/rma_management/get_rma_information/)
[Get Courtesy Refund Information](https://developer.newegg.com/newegg_marketplace_api/rma_management/get_courtesy_refund_information/)
[Get Courtesy Refund Request Status](https://developer.newegg.com/newegg_marketplace_api/rma_management/get_courtesy_refund_request_status/)
[Get Report Status](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_status/)
[Get Order List Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_order_list_report/)
[Get Settlement Summary Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_settlement_summary_report/)
[Get Settlement Transaction Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_settlement_transaction_report/)
[Get RMA List Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_rma_list_report/)
[Get Item Basic Information Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get-item-basic-information-report/)
[Get Item Lookup Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_item_lookup_report/)
[Get Daily Inventory Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_daily_inventory_report/)
[Get Daily Price Report](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_daily_price_report/)
[Campaign List](https://developer.newegg.com/newegg_marketplace_api/sponsored-ads-management/campaign-list/)
[Group List](https://developer.newegg.com/newegg_marketplace_api/sponsored-ads-management/group-list/)
[Campaign Performance Report](https://developer.newegg.com/newegg_marketplace_api/sponsored-ads-management/campaign-performance-report/)
[Get Inbound Shipment Status Request](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get_inbound_shipment_status_request/)
[Get Inbound Shipment Request Result](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get_inbound_shipment_request_result/)
[Get Inbound Shipment List](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get_inbound_shipment_list/)
[Get Warehouse List](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get-warehouse-list/)

## Troubleshooting

Max number of tables that can be synced at a time is 6,000. We advise you to adjust your settings if it fails to fetch schema due to max number of tables reached.