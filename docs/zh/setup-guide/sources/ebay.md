# eBay

此页面包含eBay的设置指南和参考信息。

## 前提条件

* eBay店铺名称
* eBay账号登录信息（用户名和密码）

## 设置指南

1. 从数据源列表中选择**eBay**。

2. 填写**数据源名称**。

3. 填写eBay**店铺名称**。

4. **验证您的eBay账户**。

5. 在**数据复制方式**中，在**根据开始日期复制**或**周期性复制**中选择。

6. 点击**保存并测试**。

## 支持的同步模式

eBay数据源支持以下同步模式：

* 完全复制
* 增量复制

## 支持的数据流

此数据源能够同步以下数据流：

* [分析（Analytics）](https://developer.ebay.com/api-docs/sell/analytics/resources/methods)
* [支出（Payouts）](https://developer.ebay.com/api-docs/sell/finances/resources/payout/methods/getPayouts)
* [交易（Transactions）](https://developer.ebay.com/api-docs/sell/finances/resources/transaction/methods/getTransactions)
* [订单（Orders）](https://developer.ebay.com/api-docs/sell/fulfillment/resources/order/methods/getOrders)
* [库存物品（Inventory Items）](https://developer.ebay.com/api-docs/sell/inventory/resources/inventory_item/methods/getInventoryItems)
* [库存地点（Inventory Locations）](https://developer.ebay.com/api-docs/sell/inventory/resources/location/methods/getInventoryLocations)
* [广告系列（Campaigns）](https://developer.ebay.com/api-docs/sell/marketing/resources/campaign/methods/getCampaigns)
* [促销（Promotions）](https://developer.ebay.com/api-docs/sell/marketing/resources/promotion/methods/getPromotions)
* [促销报告（Promotion Reports）](https://developer.ebay.com/api-docs/sell/marketing/resources/promotion_report/methods/getPromotionReports)

## 故障排除

单次可同步的最大表数为6千张。如果由于达到最大表数而无法获取数据架构，我们建议您调整数据源设置。

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |