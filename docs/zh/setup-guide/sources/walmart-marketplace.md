# 沃尔玛（Walmart Marketplace）

此页面包含沃尔玛商城（Walmart Marketplace）的设置指南和参考信息。

## 前提条件

* Client ID
* Client Secret

## 设置指南

### 第1步：获取您的沃尔玛API密钥（API key）

1. 登录您的[沃尔玛卖家控制面板（Walmart seller dashboard）](https://seller.walmart.com)。

2. 点击**Settings** -> **API Key Management**

3. 点击**Walmart Developer Portal**，您将被重定向到沃尔玛开发人员界面。

4. 记下**Production keys**选项卡内的**Client ID**和**Client secret**。这些将用于在Daspire中创建该数据源。

### 第2步：在Daspire中设置沃尔玛（Walmart）数据源

1. 从数据源列表中选择**Walmart**。

2. 填写**数据源名称（Source Name）**。

3. 填写Walmart**店铺名称（Store Name）**。

4. 填写Walmart**Client Id**.

5. 填写Walmart**Client Secret**.

6. 在获取方式（Acquisition Method）中，输入**开始时间（Start Time）**，用于从指定的开始日期开始生成报告。应采用年年年年-月月-日日（YYYY-MM-DD）格式且过去不超过60天。如果未指定，则使用今天的日期。特定配置文件的日期是根据其时区计算的，应在格林威治标准时间时区中指定此参数。由于生成当天的报告没有意义（指标可能会更改），因此它会生成前一天的报告（例如，如果开始日期是2022-10-11，它将使用20221010作为请求的reportDate参数）。

7. 点击**设置数据源**。

## 支持的同步模式

沃尔玛（Walmart）数据源支持以下同步模式：

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