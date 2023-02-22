# Shopify

此页面包含Shopify的设置指南和参考信息。

## 前提条件

* 您的Shopify商店名称
* Shopify登录信息或API密码

## 功能 

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新同步 | 支持 |
| 增量同步 - 追加同步 | 支持 |
| 命名空间 | 不支持 |

Shopify数据源支持**完全刷新复制**和**增量复制**同步。每次运行同步时，您可以选择仅复制新数据或更新数据，或您为复制设置的表和列中的所有行。

Daspire可以为[Shopify API](https://help.shopify.com/en/api/reference) 同步数据。

## 设置指南

本数据源支持API PASSWORD认证方式。

1. 前往 https://YOURSTORE.myshopify.com/admin/apps/private

2. 如果未启用，则启用私有开发。

3. 创建私有应用程序。

4. 选择您要允许访问的资源。Daspire只需要读取级别的访问权限。

  > **注意：** 用户界面将显示所有可能的数据源，如果它没有访问资源的权限，则会在同步时显示错误。

5. Admin API部分下的密码是您将用作集成的api\_password的密码。

6. 您已准备好在Daspire中设置Shopify！

## 支持的数据流

此数据源能够同步以下数据流：

* [放弃结帐（Abandoned Checkouts）](https://help.shopify.com/en/api/reference/orders/abandoned_checkouts)
* [系列（Collects）](https://help.shopify.com/en/api/reference/products/collect)
* [自定义系列（Custom Collections）](https://help.shopify.com/en/api/reference/products/customcollection)
* [客户（Customers）](https://help.shopify.com/en/api/reference/customers)
* [订单草稿（Draft Orders）](https://help.shopify.com/en/api/reference/orders/draftorder)
* [折扣码（Discount Codes）](https://shopify.dev/docs/admin-api/rest/reference/discounts/discountcode)
* [元字段（Metafields）](https://help.shopify.com/en/api/reference/metafield)
* [订单（Orders）](https://help.shopify.com/en/api/reference/order)
* [订单退款（Orders Refunds）](https://shopify.dev/api/admin/rest/reference/orders/refund)
* [订单风险（Orders Risks）](https://shopify.dev/api/admin/rest/reference/orders/order-risk)
* [产品（Products）](https://help.shopify.com/en/api/reference/products)
* [交易（Transactions）](https://help.shopify.com/en/api/reference/orders/transaction)
* [余额交易（Balance Transactions）](https://shopify.dev/api/admin-rest/2021-07/resources/transactions)
* [页面（Pages）](https://help.shopify.com/en/api/reference/online-store/page)
* [价格规则（Price Rules）](https://help.shopify.com/en/api/reference/discounts/pricerule)
* [位置（Locations）](https://shopify.dev/api/admin-rest/2021-10/resources/location)
* [库存项目（InventoryItems）](https://shopify.dev/api/admin-rest/2021-10/resources/inventoryItem)
* [库存水平（InventoryLevels）](https://shopify.dev/api/admin-rest/2021-10/resources/inventorylevel)
* [配送订单（Fulfillment Orders）](https://shopify.dev/api/admin-rest/2021-07/resources/fulfillmentorder)
* [配送（Fulfillments）](https://shopify.dev/api/admin-rest/2021-07/resources/fulfillment)
* [店铺（Shop）](https://shopify.dev/api/admin-rest/2021-07/resources/shop)

**注意**

为了获得更好的增量复制体验，建议执行以下操作：

1. 订单退款、订单风险、交易应与订单流同步。

2. 折扣代码应与价格规则流同步。

如果子流单独从父流同步 - 将进行完全同步，然后过滤掉记录。

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| string | string |
| number | number |
| array | array |
| object | object |
| boolean | boolean |

## 性能考虑

Shopify有一些[速率限制](https://shopify.dev/concepts/about-apis/rate-limits)。通常情况下，不应该存在节流或超过速率限制的问题，但在某些极端情况下，用户会收到如下警告消息：

```
Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

当数据源命中429 - 超出速率限制HTTP错误时，这是预期中的。对于给定的错误消息，同步操作仍在继续，但需要更多时间才能完成。