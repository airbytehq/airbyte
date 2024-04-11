# ShipStation

此页面包含ShipStation的设置指南和参考信息。

## 前提条件

* ShipStation API密钥（API Key）
* API秘密（API Secret）

## 功能

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新复制 | 支持 |
| 增量复制 | 支持 |
| SSL链接 | 支持 |
| 命名空间 | 不支持 |

## 设置指南

### 第一步：获取ShipStation设置相关信息

1. 登录您的ShipStation账号。

2. 点击屏幕右上角的设置按钮。
![ShipStation settings](/docs/setup-guide/assets/images/shipstation-settings.jpg "ShipStation settings")

3. 在左边的侧边栏中，点击**账号（Account）**，然后点击**API设置（API Settings）**.
![ShipStation API settings](/docs/setup-guide/assets/images/shipstation-api-settings.jpg "ShipStation API settings")

4. 复制下**API密钥（API Key）**和**API秘密（API Secret）**。

> 如果您还没有生成过API密钥，点击**生成API密钥（Generate API Keys）**按钮以获取API密钥。您可能需要[联系ShipStation客户支持](mailto:support@shipstation.com)以激活此功能。

![ShipStation API keys](/docs/setup-guide/assets/images/shipstation-api-keys.jpg "ShipStation API keys")

5. 您已成功获取了所有在Daspire设置ShipStation所需的资料。

### 第二步：在Daspire中设置数据源

1. 在数据源设置页面上，从数据源类型下拉列表中选择**ShipStation**。

2. 输入**数据源名称**。

3. 输入ShipStation**API密钥（API Key）**。

4. 输入ShipStation**API秘密（API Secret）**。

5. 如果您想从特定商店获取数据，请输入您的ShipStation**店铺ID（Store ID）**。

  > 请参阅[ShipStation文档](https://help.shipstation.com/hc/en-us/articles/4405467007771-How-do-I-access-my-Store-ID-in-ShipStation-)以了解如何在ShipStation中获取您的店铺ID。

6. 点击**保存并测试**。

## 支持的数据流

此数据源能够同步以下数据流：

* [快递运营商列表（List Carriers）](https://www.shipstation.com/docs/api/carriers/list/)
* [顾客列表（List Customers）](https://www.shipstation.com/docs/api/customers/list/)
* [配送列表（List Fulfillments）](https://www.shipstation.com/docs/api/fulfillments/list-fulfillments/)
* [产品列表（List Products）](https://www.shipstation.com/docs/api/products/list/)
* [出货列表（List Shipments）](https://www.shipstation.com/docs/api/shipments/list/)
* [获取店铺（Get Store）](https://www.shipstation.com/docs/api/stores/get-store/)
* [市场列表（List Marketplaces）](https://www.shipstation.com/docs/api/stores/list-marketplaces/)
* [店铺列表（List Stores）](https://www.shipstation.com/docs/api/stores/list/)
* [用户列表（List Users）](https://www.shipstation.com/docs/api/users/list/)
* [获取仓库（Get Warehouse）](https://www.shipstation.com/docs/api/warehouses/get/)
* [仓库列表（List Warehouses）](https://www.shipstation.com/docs/api/warehouses/list/)
* [获取订单（Get Order）](https://www.shipstation.com/docs/api/orders/get-order/)

## 故障排除

单次可同步的最大表数为6千张。如果由于达到最大表数而无法获取数据架构，我们建议您调整数据源设置。
