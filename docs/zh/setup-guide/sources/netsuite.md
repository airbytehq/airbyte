# NetSuite

此页面包含NetSuite的设置指南和参考信息。

Daspire实施[SuiteTalk REST Web服务](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/chapter_1540391670.html)并使用 REST API获取客户数据。

## 前提条件

* [Oracle NetSuite帐户](https://system.netsuite.com/pages/customerlogin.jsp?country=US)
* 允许访问所有帐户权限选项
* 领域（Realm）
* 消费者密钥（Consumer Key）
* 消费者秘密（Consumer Secret）
* Token ID
* Token Secret

## 设置指南

### 第1步：设置NetSuite帐户并获取所需信息

#### 步骤1.1：获取领域（Realm）信息

1. 登录您的[NetSuite帐户](https://system.netsuite.com/pages/customerlogin.jsp?country=US)

2. 转到**Setup** » **Company** » **Company Information**

3. 复制您的账户ID（Account ID）。您的帐户ID就是您的领域（Realm）。如果您使用普通帐户，它看起来像**1234567**，如果是测试账户，它看起来像**1234567\_SB2**

#### 步骤1.2：启用功能

1. 转到**Setup** » **Company** » **Enable Features**

2. 点击**SuiteCloud**选项卡

3. 向下滚动到**Manage Authentication**部分

4. 启用复选框**TOKEN-BASED AUTHENTICATION**

5. 保存更改

#### 步骤1.3：创建接口（获取Consumer Key和Consumer Secret）

1. 转到**Setup** » **Integration** » **Manage Integrations** » **New**

2. 填写**名称**字段。_这只是对接口的描述_

3. **State**将保持**enabled**状态

4. 在 _Authentication_ 部分启用复选框**Token-Based Authentication**

5. 保存更改

6. 之后会出现一次**Consumer Key**和**Consumer Secret**，复制它们。

#### 步骤1.4：设置角色

1. 转到**Setup** » **Users/Roles** » **Manage Roles** » **New**

2. 填写**Name**字段。

3. 向下滚动到**Permissions**标签

4. 您需要手动选择选择列表中的每条记录，并在下一个选项卡上授予**Full**级别的访问权限：（权限、报告、列表、设置、自定义记录）。在这一点上您非常需要小心。

#### 步骤1.5：设置用户

1. 转到**Setup** » **Users/Roles** » **Manage Users**

2. 在 _Name_ 列中单击您要授予访问权限的用户名

3. 然后点击用户名下的**Edit**按钮

4. 向下滚动到底部的**Access**选项卡

5. 从下拉列表中选择您在步骤**1.4**中创建的角色

6. 保存更改

#### 步骤1.6：为角色创建Access Token

1. 转到**Setup** » **Users/Roles** » **Access Tokens** » **New**

2. 选择一个**Application Name**

3. 在**User**下，选择您在步骤**1.4**中分配了 _Role_ 的用户

4. 在**Role**中选择您在步骤**1.5**中给用户分配的权限

5. 在**Token Name**下，您可以为正在创建的Token指定一个描述性名称

6. 保存更改

7. 之后会显示一次**Token ID**和**Token Secret**，复制它们。

#### 步骤1.7：总结

您已获取以下参数：

* 领域/Realm（账户ID/Account ID）
* 消费者密钥（Consumer Key）
* 消费者秘密（Consumer Secret）
* Token ID
* Token Secret 
* 此外，您还为您早先创建的用户和角色正确地配置了具有**正确权限**和**Access Token**的**帐户**。

### 第2步：在Daspire中设置数据源

1. 转到Daspire控制面板。

2. 在左侧导航栏中，点击**数据源**。在右上角，点击**添加新来源**。

3. 在数据源设置页面上，从数据源类型下拉列表中选择**NetSuite**并输入该数据源的名称。

4. 添加**领域（Realm）**

5. 添加**消费者密钥（Consumer Key）**

6. 添加**消费者秘密（Consumer Secret）**

7. 添加**Token ID**

8. 添加**Token Secret**

9. 点击设置数据源

## 支持的同步模式

NetSuite数据源支持以下同步模式：

* 完全复制
* 增量复制

## 支持的数据流

* 数据流是根据角色和用户对它们的访问权限以及帐户设置生成的，确保您使用的是管理员或授予Access Token的任何其他自定义角色，可以访问NetSuite以进行数据同步。

## 性能考虑

接口受Netsuite[每个接口的并发限制](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/bridgehead_156224824287.html)的限制。