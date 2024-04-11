# NetSuite

此页面包含NetSuite的设置指南和参考信息。

Daspire使用[SuiteTalk REST Web服务](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html)和 REST API获取客户数据。

## 前提条件

* [Oracle NetSuite帐户](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
* 允许访问所有帐户权限选项
* 领域（Realm）
* 消费者密钥（Consumer Key）
* 消费者秘密（Consumer Secret）
* 令牌ID（Token ID）
* 令牌秘密（Token Secret）
* 语言（公司的默认语言）

## 设置指南

### 第1步：设置NetSuite帐户并获取所需信息

#### 步骤1.1：获取领域（Realm）信息

1. 登录您的[NetSuite帐户](https://system.netsuite.com/pages/customerlogin.jsp?country=US)

2. 点击**设置（Setup）** » **公司（Company）** » **公司信息（Company Information）**

3. 复制您的**账户ID（Account ID）**。您的帐户ID就是您的**领域（Realm）**。如果您使用普通帐户，它看起来像**1234567**，如果是测试账户，它看起来像**1234567\_SB2**
![NetSuite Realm](/docs/setup-guide/assets/images/netsuite-realm.jpg "NetSuite Realm")

#### 步骤1.2：启用功能

1. 转到**设置（Setup）** » **公司（Company）** » **启用功能（Enable Features）**

2. 点击**SuiteCloud**选项卡

3. 向下滚动到**管理身份验证	（Manage Authentication）**部分

4. 启用复选框**基于令牌的身份验证（TOKEN-BASED AUTHENTICATION）**

5. 保存更改
![NetSuite Token Based Auth](/docs/setup-guide/assets/images/netsuite-token-based-auth.jpg "NetSuite Token Based Auth")

#### 步骤1.3：创建接口（获取Consumer Key和Consumer Secret）

1. 转到**设置（Setup）** » **集成（Integration）** » **管理集成（Manage Integrations）** » **新建（New）**

2. 填写**名称**字段。_这是对集成的描述_

3. **状态（State）**保持**已启用（enabled）**状态

4. 设置您的**并发限制**，并确保它等于或小于**最大并发性限制**

5. 在**验证（Authentication）**部分启用复选框**基于令牌的身份验证（Token-Based Authentication）**

6. 保存更改

7. 之后会出现一次**消费者密钥（Consumer Key）**和**消费者秘密（Consumer Secret）**，复制它们。
![NetSuite Integration](/docs/setup-guide/assets/images/netsuite-integration.jpg "NetSuite Integration")

#### 步骤1.4：设置角色

1. 转到**设置（Setup）** » **用户/角色（Users/Roles）** » **管理角色（Manage Roles）** » **新建（New）**

2. 填写**名称（Name）**字段。

3. 向下滚动到**权限（Permissions）**部分

4. 您需要手动选择选择列表中的每条记录，并在下一个选项卡上授予**全部（Full）**级别的访问权限：（事务处理、报告、列表、设置、自定义记录）。在这一点上您非常需要注意。
![NetSuite Setup Role](/docs/setup-guide/assets/images/netsuite-setup-role.jpg "NetSuite Setup Role")

#### 步骤1.5：设置用户

1. 转到**设置（Setup）** » **用户/角色（Users/Roles）** » **管理用户（Manage Users）**

2. 在**名称（Name）**列中单击您要授予访问权限的用户名

3. 然后点击用户名下的**编辑（Edit）**按钮

4. 向下滚动到底部的**访问权限（Access）**选项卡

5. 从下拉列表中选择您在步骤**1.4**中创建的角色

6. 保存更改
![NetSuite Setup User](/docs/setup-guide/assets/images/netsuite-setup-user.jpg "NetSuite Setup User")

#### 步骤1.6：为角色创建访问令牌（Access Tokens）

1. 转到**设置（Setup）** » **用户/角色（Users/Roles）** » **访问令牌（Access Tokens）** » **新建（New）**

2. 选择一个**应用程序名称（Application Name）**

3. 在**用户（User）**中，选择您在步骤**1.4**中分配了**权限（Role）**的用户

4. 在**角色（Role）**中，选择您在步骤**1.5**中给用户分配的权限

5. 在**令牌名称（Token Name）**中，您可以为正在创建的令牌指定一个描述性名称

6. 保存更改

7. 之后会显示一次**令牌ID（Token ID）**和**令牌秘密（Token Secret）**，复制它们。
![NetSuite Access Token](/docs/setup-guide/assets/images/netsuite-access-token.jpg "NetSuite Access Token")

#### 步骤 1.7：获取公司的默认语言

1. 转到**设置（Setup）** » **设置管理器（Setup Manager）** » **公司（Company）** » **常规首选项（General Preference）**

2. 单击**语言（Language）**选项卡

3. 您会在这里找到公司的默认语言
![NetSuite Default Company Language](/docs/setup-guide/assets/images/netsuite-default-company-language.jpg "NetSuite Default Company Language")

#### 步骤1.8：总结

您已获取以下参数：

* 领域/Realm（账户ID/Account ID）
* 消费者密钥（Consumer Key）
* 消费者秘密（Consumer Secret）
* 令牌ID（Token ID）
* 令牌秘密（Token Secret）
* 公司的默认语言
* 此外，您还为您早先创建的用户和角色正确地配置了具有**正确权限**和**访问令牌（Access Token）**的**帐户**

### 第2步：在Daspire中设置数据源

1. 转到Daspire控制面板。

2. 在左侧导航栏中，点击**数据源**。在右上角，点击**添加新数据源**。

3. 在数据源设置页面上，从数据源类型下拉列表中选择**NetSuite**并输入该数据源的名称。

4. 添加**领域（Realm）**

5. 添加**消费者密钥（Consumer Key）**

6. 添加**消费者秘密（Consumer Secret）**

7. 添加**令牌ID（Token ID）**

8. 添加**令牌秘密（Token Secret）**

9. 添加**语言**

10. 添加**对象类型**

11. 添加**开始日期**

12. 点击**保存并测试**

## 支持的同步模式

NetSuite数据源支持以下同步模式：

* 完全复制
* 增量复制

## 支持的数据流

* 数据流是根据角色和用户对它们的访问权限以及帐户设置生成的，确保您使用的是管理员或授予访问令牌的任何其他自定义角色，可以访问NetSuite以进行数据同步。

## 性能考虑

1. 此接口受Netsuite[单个接口的并发限制](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_156224824287.html)的限制。如果达到并发限制，同步可能暂停或失败。

  > 您可以在**设置（Setup）** » **集成（Integration）** » **集成治理（Integration Goverance）**中找到每个集成的并发限制。在**并发用量（Concurrency Usage）**部分，您可以查看帐户并发限制和未分配的并发限制。

2. 如果由于并发限制导致同步失败，您可以尝试重新同步至同步成功。

3. 您也可以联系NetSuite客户支持[更改您的并发限制](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_164095787873.html#:~:text=By%20default%2C%20NetSuite%20Connector%20limits,limit%2C%20contact%20NetSuite%20Customer%20Support)。

## 故障排除

单次可同步的最大表数为6千张。如果由于达到最大表数而无法获取数据架构，我们建议您调整数据源设置。