# eBay

此页面包含eBay的设置指南和参考信息。

## 前提条件

* Client ID
* Client Secret
* Refresh Token

## 设置指南

### 第1步：获取eBay API密钥

1. 登录eBay开发者账号并导航至**您的帐户 > 应用程序密钥（Application Keys）**。

2. 在Application Keys页面上，获取**Production environment**的**App ID（Client ID）**、**Cert ID（Client Secret）**和**Refresh Token** 值。这些将用于在Daspire中创建该接口。

### 第2步：在Daspire中设置eBay数据源

1. 从数据源列表中选择**eBay**。

2. 填写**数据源名称（Source Name）**。

3. 填写eBay**店铺名称（Store Name）**。

4. 填写eBay**Client Id**.

5. 填写eBay**Client Secret**.

6. 填写eBay**Refresh Token**.

7. 在获取方式（Acquisition Method）中，输入**开始时间（Start Time）**，用于从指定的开始日期开始生成报告。应采用年年年年-月月-日日（YYYY-MM-DD）格式且过去不超过60天。如果未指定，则使用今天的日期。特定配置文件的日期是根据其时区计算的，应在格林威治标准时间时区中指定此参数。由于生成当天的报告没有意义（指标可能会更改），因此它会生成前一天的报告（例如，如果开始日期是2022-10-11，它将使用20221010作为请求的reportDate参数）。

8. 点击**设置数据源**。

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

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |