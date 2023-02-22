# 亚马逊广告（Amazon Ads）

此页面包含亚马逊广告（Amazon Ads）的设置指南和参考信息。

## 前提条件

* 亚马逊广告账号登录信息（用户名和密码）
* 店铺名称（Store Name）
* 区域（Region）

## 设置指南

### 第1步：设置亚马逊广告

创建一个可以访问[亚马逊广告账户](https://advertising.amazon.com/)的亚马逊用户。

### 第2步：在Daspire中设置亚马逊广告数据源

1. 从数据源列表中选择**亚马逊广告（Amazon Ads）**。

2. 填写**数据源名称**。

3. **验证您的亚马逊广告账户**。

4. 填写亚马逊**店铺名称**。

5. 在**区域**中选择从**北美**、**欧洲**或**远东**提取数据。更详细信息，请参阅[亚马逊文档](https://advertising.amazon.com/API/docs/en-us/info/api-overview#api-endpoints)。

6. **报告等待时限**是接口等待为数据流品牌报告、品牌视频报告、显示报告、产品报告生成报告的最大分钟数。

7. **生成报告最多重试次数**是接口尝试生成报告的最多尝试次数。

8. **开始日期**（可选），用于从指定的开始日期开始生成报告。应采用年年年年-月月-日日（YYYY-MM-DD）格式且过去不超过60天。如果未指定，则使用今天的日期。特定配置文件的日期是根据其时区计算的，应在格林威治标准时间时区中指定此参数。由于生成当天的报告没有意义（指标可能会更改），因此它会生成前一天的报告（例如，如果开始日期是2022-10-11，它将使用20221010作为请求的reportDate参数）。

9. 您要为其获取数据的**档案ID（Profile IDs）**（可选）。更详细信息，请参阅[亚马逊文档](https://advertising.amazon.com/API/docs/en-us/concepts/authorization/profiles)。

10. 点击**设置数据源**。

## 支持的同步模式

亚马逊广告数据源支持以下同步模式：

* 完全复制
* 增量复制

## 支持的数据流

此数据源能够同步以下数据流：

* [档案（Profiles）](https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles)
* [赞助品牌广告系列（Sponsored Brands Campaigns）](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Campaigns)
* [赞助品牌广告组（Sponsored Brands Ad groups）](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Ad%20groups)
* [赞助品牌关键词（Sponsored Brands Keywords）](https://advertising.amazon.com/API/docs/en-us/sponsored-brands/3-0/openapi#/Keywords)
* [赞助品牌报告（Sponsored Brands Reports）](https://advertising.amazon.com/API/docs/en-us/reference/sponsored-brands/2/reports)
* [赞助展示广告系列（Sponsored Display Campaigns）](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Campaigns)
* [赞助展示广告组（Sponsored Display Ad groups）](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Ad%20groups)
* [赞助展示产品广告（Sponsored Display Product Ads）](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Product%20ads)
* [赞助商展示目标受众（Sponsored Display Targetings）](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Targeting)
* [赞助展示报告（Sponsored Display Reports）](https://advertising.amazon.com/API/docs/en-us/sponsored-display/3-0/openapi#/Reports)
* [赞助产品广告系列（Sponsored Products Campaigns）](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Campaigns)
* [赞助产品广告组（Sponsored Products Ad groups）](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Ad%20groups)
* [赞助产品关键字（Sponsored Products Keywords）](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Keywords)
* [赞助产品否定关键词（Sponsored Products Negative keywords）](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Negative%20keywords)
* [赞助产品广告（Sponsored Products Ads）](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20ads)
* [赞助产品目标受众（Sponsored Products Targetings）](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Product%20targeting)
* [赞助产品报告（Sponsored Products Reports）](https://advertising.amazon.com/API/docs/en-us/sponsored-products/2-0/openapi#/Reports)

## 注意事项

所有报告都是在相对于目标配置文件的时区的前一天生成的。

## 性能考虑

您可以在[此处](https://advertising.amazon.com/API/docs/en-us/get-started/developer-notes)找到有关预期报告生成等待时间的信息。

## 数据类型映射

| 集成类型 | Daspire类型 |
| --- | --- |
| `string` | `string` |
| `int`, `float`, `number` | `number` |
| `date` | `date` |
| `datetime` | `datetime` |
| `array` | `array` |
| `object` | `object` |