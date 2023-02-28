# 亚马逊卖家合作伙伴（Amazon Seller Partner）

此页面包含亚马逊卖家合作伙伴 (Amazon Seller Partner / Amazon SP) 的设置指南和参考信息。

## 前提条件

* 店铺名称
* 应用ID
* 亚马逊卖家合作伙伴账号
* AWS访问密钥
* AWS秘密访问密钥
* 亚马逊资源名称角色
* AWS环境
* AWS区域

## 设置指南

### 第1步：设置亚马逊卖家合作伙伴

[注册](https://developer-docs.amazon.com/sp-api/docs/registering-your-application)亚马逊卖家合作伙伴申请。
[创建](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html)IAM用户.

### 第1步：在Daspire中设置亚马逊卖家合作伙伴数据源

1. 从数据源列表中选择**亚马逊卖家合作伙伴（Amazon Seller Partner）**。

2. 填写**数据源名称**。

3. 填写亚马逊**店铺名称**。

4. 填写亚马逊**应用ID**。

5. **验证您的亚马逊广告账户**。

6. 填写**AWS访问密钥**。

7. 填写**AWS秘密访问密钥**。

8. 填写亚马逊**资源名称角色**。

9. 选择**AWS环境**。

10. **报告等待时限**是接口等待为数据流品牌报告、品牌视频报告、显示报告、产品报告生成报告的最大分钟数。

11. **期间天数**持切片增量同步的报告没有更新状态时，将用于初始完全刷新同步的数据流切片。

12. 选择**AWS区域**。

13. **结束日期**（可选） - 不会复制此日期之后的任何数据。

14. **开始日期** - 此日期之前的任何数据都不会被复制。

15. **报告选项**是传递给报告的附加信息。必须是有效的json字符串。

16. 点击**设置数据源**。

## 支持的同步模式

亚马逊卖家合作伙伴（Amazon SP）数据源支持以下同步模式：

* 完全复制
* 增量复制

## 支持的数据流

此数据源能够同步以下数据流：

* [FBA库存报告（FBA Inventory Reports）](https://sellercentral.amazon.com/gp/help/200740930)
* [FBA订单报告（FBA Orders Reports）](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989110)
* [FBA发货报告（FBA Shipments Reports）](https://sellercentral.amazon.com/gp/help/help.html?itemID=200989100)
* [FBA换货报告（FBA Replacements Report）](https://sellercentral.amazon.com/help/hub/reference/200453300)
* [FBA仓储费报告（FBA Storage Fees Report）](https://sellercentral.amazon.com/help/hub/reference/G202086720)
* [补充库存报告（Restock Inventory Reports）](https://sellercentral.amazon.com/help/hub/reference/202105670)
* [文件打开列表报告（Flat File Open Listings Reports）](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [文件订单报告（Flat File Orders Reports）](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [文件订单报告最近更新（Flat File Orders Reports By Last Update）](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)（增量）
* [FBA发货报告（Amazon-Fulfilled Shipments Report）](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [商家列表报告（Merchant Listings Reports）](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [供应商直接履行配送（Vendor Direct Fulfillment Shipping）](https://developer-docs.amazon.com/sp-api/docs/vendor-direct-fulfillment-shipping-api-v1-reference)
* [供应商库存健康报告（Vendor Inventory Health Reports）](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)
* [订单（Orders）](https://developer-docs.amazon.com/sp-api/docs/orders-api-v0-reference)（增量）
* [卖家反馈报告（Seller Feedback Report）](https://developer-docs.amazon.com/sp-api/docs/reports-api-v2021-06-30-reference)（增量）
* [品牌分析替代购买报告（Brand Analytics Alternate Purchase Report）](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [品牌分析项目比较报告（Brand Analytics Item Comparison Report）](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [品牌分析市场购物车报告（Brand Analytics Market Basket Report）](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [品牌分析重复购买报告（Brand Analytics Repeat Purchase Report）](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [品牌分析搜索词报告（Brand Analytics Search Terms Report）](https://developer-docs.amazon.com/sp-api/docs/report-type-values#brand-analytics-reports)
* [浏览记录报告（Browse tree report）](https://github.com/amzn/selling-partner-api-docs/blob/main/references/reports-api/reporttype-values.md#browse-tree-report)
* [财务事件组（Financial Event Groups）](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialeventgroups)
* [财务事件（Financial Events）](https://developer-docs.amazon.com/sp-api/docs/finances-api-reference#get-financesv0financialevents)

## 报告选项

确保在已配置报告的报告选项设置中配置[必需参数](https://developer-docs.amazon.com/sp-api/docs/report-type-values)。

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |