# Shopify

此页面包含Shopify的设置指南和参考信息。

## 前提条件

* 您的Shopify店铺名称
* Shopify登录信息或API密码

## 功能 

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新复制 | 支持 |
| 增量复制 - 追加同步 | 支持 |
| 命名空间 | 不支持 |

Shopify数据源支持**完全刷新复制**和**增量复制**同步。每次运行同步时，您可以选择仅复制新数据或更新数据，或您为复制设置的表和列中的所有行。

Daspire可以为[Shopify API](https://help.shopify.com/en/api/reference) 同步数据。

## 设置指南

### 使用API密码设置

1. 前往https://admin.shopify.com/store/YOURSTORE ，点击侧边栏的**设置（Settings）**按钮。
![Shopify Store Settings](/docs/setup-guide/assets/images/shopify-settings.jpg "Shopify Store Settings")

2. 点击侧边栏的**应用程序和销售渠道（Apps and sales channels）**，然后点击**开发应用程序（Develop apps）**。
![Shopify Develop Apps](/docs/setup-guide/assets/images/shopify-develop-apps.jpg "Shopify Develop Apps")

3. 点击**创建应用（Create an app）**创建私有应用。
![Shopify Create an App](/docs/setup-guide/assets/images/shopify-create-app.jpg "Shopify Create an App")

4. 填写**应用名称*（App name）**并选择**应用开发者（App developer）**.
![Shopify Create an App](/docs/setup-guide/assets/images/shopify-create-app2.jpg "Shopify Create an App")

5. 打开您刚刚创建的应用，点击**配置*（Configuration）**，然后点击**管理API集成（Admin API integration）**中的**配置（Configure）**。
![Shopify Config](/docs/setup-guide/assets/images/shopify-configuration.jpg "Shopify Config")

4. 在**管理API访问权限（Admin API access scopes）**中，选择您要允许访问的资源。Daspire只需要读取级别的访问权限。选择完成后，点击**保存（Save）**。

  > **注意：** 用户界面将显示所有可能的数据源，如果它没有访问资源的权限，则会在同步时显示错误。

![Shopify Access Scopes](/docs/setup-guide/assets/images/shopify-access-scopes.jpg "Shopify Access Scopes")

7. 在为应用程序分配相关访问范围后，点击**API凭据（API credentials）**，然后点击**安装应用（Install app）**. 
![Shopify API Credentials](/docs/setup-guide/assets/images/shopify-api-creds.jpg "Shopify API Credentials")

8. 安装应用程序后，您的**管理API访问令牌（Admin API access token）**将会显示，复制它。您的API访问令牌以 ***shpat_***开头。您将用作集成的api\_password的密码。
![Shopify API Access Token](/docs/setup-guide/assets/images/shopify-api-access-token.jpg "Shopify API Access Token")

9. 您已准备好在Daspire中设置Shopify！

### 在Daspire中设置Shopify

1. 从数据源列表中选择 **Shopify**。

2. 输入一个**数据源名称**。

3. 输入您的Shopify**店铺名称**。

4. 使用OAuth 2.0，**验证您的Shopify帐户**，或使用API密码，输入您的**API密码**。

5. 输入**复制开始日期** - 您希望复制数据的开始日期。

6. 点击**保存并测试**。

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
| `string` | `string` |
| `number` | `number` |
| `array` | `array` |
| `object` | `object` |
| `boolean` | `boolean` |

## 性能考虑

Shopify有一些[速率限制](https://shopify.dev/concepts/about-apis/rate-limits)。通常情况下，不应该存在节流或超过速率限制的问题，但在某些极端情况下，用户会收到如下警告消息：

```
Caught retryable error '<some_error> or null' after <some_number> tries. Waiting <some_number> seconds then retrying..."
```

当数据源命中429 - 超出速率限制HTTP错误时，这是预期中的。对于给定的错误消息，同步操作仍在继续，但需要更多时间才能完成。

## 故障排除

单次可同步的最大表数为6千张。如果由于达到最大表数而无法获取数据架构，我们建议您调整数据源设置。