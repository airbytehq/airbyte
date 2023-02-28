# BigCommerce

此页面包含BigCommerce的设置指南和参考信息。

## 功能

| 功能 | 是否支持 |
| --- | --- |
| 完全更新同步 | 支持 |
| 增量 - 追加同步 | 支持 |
| 命名空间 | 不支持 |

## 设置指南

1. 导航到您店铺的控制面板（Advanced Settings \> API Accounts \> Create API Account）

2. 创建一个API帐户。

3. 选择您要允许访问的资源。Daspire只需要读取级别的访问权限。

  > **注意：** 用户界面将显示所有可能的数据源，如果它没有访问资源的权限，则会在同步时显示错误。

4. 生成的刷新令牌将用作接口的access\_token。

5. 您已准备好在Daspire中设置BigCommerce！

## 同步概览

BigCommerce数据源支持**完全刷新复制**和**增量复制**同步。每次运行同步时，您可以选择仅复制新数据或更新数据，或您为复制设置的表和列中的所有行。

Daspire可以为[BigCommerce API](https://developer.bigcommerce.com/api-docs/getting-started/making-requests)同步数据。

## 支持的数据流

此数据源能够同步以下数据流：

* [顾客（Customers）](https://developer.bigcommerce.com/api-reference/store-management/customers-v3/customers/customersget)
* [订单（Orders）](https://developer.bigcommerce.com/api-reference/store-management/orders/orders/getallorders)
* [交易（Transactions）](https://developer.bigcommerce.com/api-reference/store-management/order-transactions/transactions/gettransactions)
* [页面（Pages）](https://developer.bigcommerce.com/api-reference/store-management/store-content/pages/getallpages)
* [产品（Products）](https://developer.bigcommerce.com/api-reference/store-management/catalog/products/getproducts)

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |

## 性能考虑

BigCommerce有一些[速率限制](https://developer.bigcommerce.com/api-docs/getting-started/best-practices).