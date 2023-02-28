# 沃尔玛商城（Walmart Marketplace）

此页面包含沃尔玛商城（Walmart Marketplace）的设置指南和参考信息。

## 前提条件

* 客户ID（Client ID）
* 客户秘密（Client Secret）

## 设置指南

### 第1步：获取您的沃尔玛API密钥

1. 登录您的[沃尔玛卖家后台（Walmart seller dashboard）](https://seller.walmart.com)。

2. 点击**Settings** -> **API Key Management**

3. 点击**Walmart Developer Portal**，您将被重定向到沃尔玛开发人员界面。

4. 记下**Production keys**选项卡内的**Client ID**和**Client secret**。这些将用于在Daspire中创建该数据源。

### 第2步：在Daspire中设置沃尔玛数据源

1. 从数据源列表中选择**沃尔玛商城（Walmart Marketplace）**。

2. 填写**数据源名称**。

3. 填写沃尔玛**店铺名称**。

4. 填写沃尔玛**Client Id**.

5. 填写沃尔玛**Client Secret**.

6. 在**数据复制方式**中，在**根据开始日期复制**或**周期性复制**中选择。

7. 点击**设置数据源**。

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
* [商品报告（Items Reports）](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [Buybox报告（Buybox Reports）](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [CPA报告（CPA Reports）](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [商品性能报告（Item Performance Reports）](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [退货替代报告（Return Overrides Reports）](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [临时报告（Promp Reports）](https://developer.walmart.com/api/us/mp/reports#operation/getItemReport)
* [获取发货（Get Shipments）](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipments)
* [获取入库货品（Get Inbound Shipment Items）](https://developer.walmart.com/api/us/mp/fulfillment#operation/getInboundShipmentItems)
* [所有部门（All Departments）](https://developer.walmart.com/api/us/mp/utilities#operation/getDepartmentList)

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |