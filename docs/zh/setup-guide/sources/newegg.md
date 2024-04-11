# Newegg

此页面包含Newegg的设置指南和参考信息。

## 前提条件


## 功能 

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新复制 | 支持 |
| SSL链接 | 支持 |
| 命名空间 | 不支持 |

## 设置指南

### 第一步：获取Newegg设置相关信息

1. 登录您的Newegg账号。

2. 

5. 您已成功获取了所有在Daspire设置Newegg所需的资料。

### 第二步：在Daspire中设置数据源

1. 在数据源设置页面上，从数据源类型下拉列表中选择**Newegg**。

2. 输入**数据源名称**。

3. 输入Newegg

4. 输入Newegg

5. 在**数据复制方式**中，在**根据开始日期复制**或**周期性复制**中选择。

6. 点击**保存并测试**。

## 支持的数据流

此数据源能够同步以下数据流：

[获取物品库存（Get Item Inventory）](https://developer.newegg.com/newegg_marketplace_api/item_management/get_inventory/)
[获取批量库存（Get Batch Inventory）](https://developer.newegg.com/newegg_marketplace_api/item_management/get-batch-inventory/)
[获取商品价格（Get Item Price）](https://developer.newegg.com/newegg_marketplace_api/item_management/get_price/)
[获取批量价格（Get Batch Price）](https://developer.newegg.com/newegg_marketplace_api/item_management/get-batch-price/)
[获取订单信息（Get Order Information）](https://developer.newegg.com/newegg_marketplace_api/order_management/get_order_information/)
[获取额外订单信息（Get Additional Order Information）](https://developer.newegg.com/newegg_marketplace_api/order_management/get_additional_order_information/)
[获取RMA信息（Get RMA Information）](https://developer.newegg.com/newegg_marketplace_api/rma_management/get_rma_information/)
[获取礼遇退款信息（Get Courtesy Refund Information）](https://developer.newegg.com/newegg_marketplace_api/rma_management/get_courtesy_refund_information/)
[获取礼遇退款请求状态（Get Courtesy Refund Request Status）](https://developer.newegg.com/newegg_marketplace_api/rma_management/get_courtesy_refund_request_status/)
[获取报告状态（Get Report Status）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_status/)
[获取订单列表报告（Get Order List Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_order_list_report/)
[获取结算摘要报告（Get Settlement Summary Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_settlement_summary_report/)
[获取结算交易报告（Get Settlement Transaction Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_settlement_transaction_report/)
[获取RMA清单报告（Get RMA List Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_rma_list_report/)
[获取商品基本信息报告（Get Item Basic Information Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get-item-basic-information-report/)
[获取商品查询报告（Get Item Lookup Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_item_lookup_report/)
[获取每日库存报告（Get Daily Inventory Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_daily_inventory_report/)
[获取每日价格报告（Get Daily Price Report）](https://developer.newegg.com/newegg_marketplace_api/reports_management/get_report_result/get_daily_price_report/)
[活动列表（Campaign List）](https://developer.newegg.com/newegg_marketplace_api/sponsored-ads-management/campaign-list/)
[组列表（Group List）](https://developer.newegg.com/newegg_marketplace_api/sponsored-ads-management/group-list/)
[活动绩效报告（Campaign Performance Report）](https://developer.newegg.com/newegg_marketplace_api/sponsored-ads-management/campaign-performance-report/)
[获取入站货件状态请求（Get Inbound Shipment Status Request）](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get_inbound_shipment_status_request/)
[获取入库货件请求结果（Get Inbound Shipment Request Result）](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get_inbound_shipment_request_result/)
[获取入库货件列表（Get Inbound Shipment List）](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get_inbound_shipment_list/)
[获取仓库列表（Get Warehouse List）](https://developer.newegg.com/newegg_marketplace_api/sbn_shipped_by_newegg_management/get-warehouse-list/)

## 故障排除

单次可同步的最大表数为6千张。如果由于达到最大表数而无法获取数据架构，我们建议您调整数据源设置。