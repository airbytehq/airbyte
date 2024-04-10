# 沃尔玛商城（Walmart Marketplace）

此页面包含沃尔玛商城（Walmart Marketplace）的设置指南和参考信息。

## 前提条件

* 客户ID（Client ID）
* 客户端密码（Client Secret）

## 设置指南

### 第1步：获取您的沃尔玛API密钥

1. 登录您的[沃尔玛卖家后台（Walmart seller dashboard）](https://seller.walmart.com)。

2. 点击**Settings** -> **API Key Management**
![Walmart Settings](/docs/setup-guide/assets/images/walmart-settings.jpg "Walmart Settings")

3. 在API Integrations页面，点击**API Key Management**，您将被重定向到沃尔玛开发人员界面。
![Walmart API Key Management](/docs/setup-guide/assets/images/walmart-api-key-mgnt.jpg "Walmart API Key Management")

4. 记下 ***Production keys***选项卡内，***My API Key***部分的客户端ID（**Client ID**）和客户端密码（**Client secret**）。这些将用于在Daspire中创建该数据源。
![Walmart API Key](/docs/setup-guide/assets/images/walmart-api-key.jpg "Walmart API Key")

### 第2步：在Daspire中设置沃尔玛数据源

1. 从数据源列表中选择**沃尔玛商城（Walmart Marketplace）**。

2. 填写**数据源名称**。

3. 填写沃尔玛**店铺名称**。

4. 填写沃尔玛**客户端ID**.

5. 填写沃尔玛**客户端密码**.

6. 在**数据复制方式**中，在**根据开始日期复制**或**周期性复制**中选择。

7. 点击**保存并测试**。

## 支持的同步模式

沃尔玛商城（Walmart Marketplace）数据源支持以下同步模式：

* 完全复制
* 增量复制

## 支持的数据流

此数据源能够同步以下数据流：

* [商品（Items）](https://developer.walmart.com/api/us/mp/items#operation/getAllItems)
* [订单（Orders）](https://developer.walmart.com/api/us/mp/orders#operation/getAllOrders)
* [退货（Returns）](https://developer.walmart.com/api/us/mp/returns#operation/getReturns)
* [所有运输节点的多项目库存（Multiple Item Inventory for All Ship Nodes）](https://developer.walmart.com/api/us/mp/inventory#operation/getMultiNodeInventoryForAllSkuAndAllShipNodes)
* [WFS库存（WFS Inventory）](https://developer.walmart.com/api/us/mp/inventory#operation/getWFSInventory)
* [获取发货（Get Shipments）](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipments)
* [获取入库货品（Get Inbound Shipment Items）](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipmentItems)
* [所有部门（All Departments）](https://developer.walmart.com/api/us/mp/utilities#operation/getDepartmentList)

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
