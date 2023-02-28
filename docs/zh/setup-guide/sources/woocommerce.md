# WooCommerce

此页面包含WooCommerce的设置指南和参考信息。

## 功能

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新同步 | 支持 |
| 增量同步 - 追加同步 | 支持 |
| 命名空间 | 不支持 |

## 设置指南

1. 导航到您店铺的WordPress管理界面，转到WooCommerce \> Settings \> Advanced \> REST API。

2. 点击“Add Key”生成API Key。

3. 选择此REST API密钥的访问级别，可以是读访问、写访问或读/写访问。Daspire只需要读取级别的访问权限。

  > **注意：**用户界面将显示所有可能的数据源，如果它没有访问资源的权限，则会在同步时显示错误。

4. Consumer Key和Consumer Secret这两个密钥是您将分别用作接口的api\_key和api\_secret。

5. 您已准备好在Daspire中设置WooCommerce！

## 同步概述

WooCommerce数据源支持**完全刷新复制**和**增量复制**。每次运行同步时，您可以选择仅复制新数据或更新数据，或您为复制设置的表和列中的所有行。

Daspire可以为[WooCommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/)同步数据。

## 支持的数据流

此数据源能够同步以下数据流：

* [顾客（Customers）](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-customers)
* [订单（Orders）](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-orders)
* [优惠券（Coupons）](https://woocommerce.github.io/woocommerce-rest-api-docs/#list-all-coupons)

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |