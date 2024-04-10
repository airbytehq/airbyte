# Shein

此页面包含Shein的设置指南和参考信息。

## 前提条件

* Shein的接入账号
* openKeyId
* secretKey

## 功能 

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新复制 | 支持 |
| SSL链接 | 支持 |
| 命名空间 | 不支持 |

## 设置指南

### 第一步：获取Shein设置相关信息

1. 申请开通Shein的[接入账号](https://openapi-portal.sheincorp.com/#/home/1/999999)

2. 获取**openKeyId**和**secretKey**，复制这两项内容，您将使用这些信息在Daspire中创建Shein数据源。

3. 您已成功获取了所有在Daspire设置Shein所需的资料。

### 第二步：在Daspire中设置数据源

1. 在数据源设置页面上，从数据源类型下拉列表中选择**Shein**。

2. 输入**数据源名称**。

3. 输入Shein **openKeyId**。

4. 输入Shein **secretKey**。

5. 在**数据复制方式**中，在**根据开始日期复制**或**周期性复制**中选择。

6. 点击**保存并测试**。

## 支持的数据流

此数据源能够同步以下数据流：

* [订单（Order）](https://openapi-portal.sheincorp.com/#/home/2/1)

## 故障排除

单次可同步的最大表数为6千张。如果由于达到最大表数而无法获取数据架构，我们建议您调整数据源设置。