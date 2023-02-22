# MySQL

此页面包含MySQL的设置指南和参考信息。

此目的地有两种类型的链接：

1. destination-mysql：支持SSL和非SSL链接。
2. destination-mysql-strict-encrypt：与上面的链接非常相似，但仅支持SSL链接。

## 前提条件

* 通过**数据规范化**将数据同步到MySQL，需MySQL8.0.0或更高版本
* **无需数据规范化**将数据同步到MySQL，需MySQL5.0或更高版本。
* 主机
* 端口
* 数据库
* 用户名
* 密码

### 权限

您将需要一个具有`CREATE, INSERT, SELECT, DROP`权限的MySQL用户。我们强烈建议为此创建一个特定于Daspire的用户。

### 网络访问

确保Daspire可以访问您的MySQL数据库。如果您的数据库位于VPC内，您可能需要允许从您用于公开Daspire的IP进行访问。

### 目标数据库

MySQL不区分数据库和模式。数据库本质上是所有表所在的架构。您需要选择现有数据库或创建新数据库。这将充当默认数据库/模式，如果数据源不提供命名空间，将在其中创建表。

## 功能

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新同步 | 支持 |
| 增量同步 - 追加同步 | 支持 |
| 增量同步 - 去重历史 | 不支持 |
| 命名空间 | 支持 |
| SSH隧道连接 | 支持 |

### 输出模式

每个数据流将输出到MySQL中它自己的表中。每个表将包含3列：

* `_daspire_ab_id`：Daspire分配给每个处理事件的uuid MySQL中的列类型是`VARCHAR(256)`。

* `_daspire_emitted_at`：表示事件何时从数据源中提取的时间戳。MySQL中的列类型是`TIMESTAMP(6)`。

* `_daspire_data`：表示事件数据的json blob。MySQL中的列类型是 `JSON`。

## 设置指南

在Daspire中设置MySQL目的地之前，您需要将[local_infile](https://dev.mysql.com/doc/refman/8.0/en/server-system-variables.html#sysvar_local_infile)系统变量设置为true。您可以通过具有[SYSTEM\_VARIABLES\_ADMIN](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#priv_system-variables-admin)权限的用户，使用`SET GLOBAL local_infile = true`这个操作运行。这是必需的，因为Daspire使用`LOAD DATA LOCAL INFILE`将数据加载到表中。

您现在应该具备将MySQL配置为用户界面中的目标所需的所有要求。您需要以下信息来配置MySQL目的地：

* **主机（Host）**
* **端口（Port）**
* **用户名（Username）**
* **密码（Password）**
* **数据库（Database）**
* **jdbc\_url\_params**（可选）

### 默认JDBC URL参数

以下JDBC URL参数由Daspire设置，不能被`jdbc_url_params`字段覆盖：

* `useSSL=true`（除非`ssl`设置为false）
* `requireSSL=true`（除非`ssl`设置为false）
* `verifyServerCertificate=false`（除非`ssl`设置为false）
* `zeroDateTimeBehavior=convertToNull`

## 限制

请注意，MySQL文档使用`lower_case_table_names`系统变量讨论标识符区分大小写。他们的建议之一是：

```
“最好采用一致的约定，例如始终使用小写名称创建和引用数据库和表。
建议使用此约定以获得最大的便携性和易用性。”
（"It is best to adopt a consistent convention, such as always creating and referring to databases and tables using lowercase names.
This convention is recommended for maximum portability and ease of use."）
``` 
[数据源：MySQL文档](https://dev.mysql.com/doc/refman/8.0/en/identifier-case-sensitivity.html)

因此，Daspire MySQL目的地强制所有标识符（表、模式和列）名称为小写。

## 通过SSH隧道连接

Daspire能够通过SSH隧道连接到MySQL实例。您可能想要这样做的原因是不可能（或违反安全策略）直接连接到数据库（例如，它没有公共IP地址）。

使用SSH隧道时，您正在配置Daspire以连接到可以直接访问数据库的中间服务器（也称为堡垒服务器）。Daspire连接到堡垒，然后要求堡垒直接连接到服务器。

使用此功能需要在创建目标时进行额外配置。我们将讨论每个配置的含义。

1. 像往常一样配置目的地的所有字段，`SSH Tunnel Method`除外。

2. `SSH Tunnel Method`默认为`No Tunnel`（即直接连接）。如果您想使用SSH隧道，请选择`SSH Key Authentication`或`Password Authentication`。

  * 如果您将使用RSA私钥作为建立SSH隧道的秘密，请选择`Key Authentication`（有关生成此密钥的更多信息，请参见下文）。

  * 如果您将使用密码作为建立SSH隧道的秘密，请选择`Password Authentication`。

3. `SSH Tunnel Jump Server Host`是指Daspire将要连接的中间（堡垒）服务器。这应该是主机名或IP地址。

4. `SSH Connection Port`是堡垒服务器上建立SSH连接的端口。SSH连接的默认端口是`22`，因此除非您明确更改了某些内容，否则请使用默认端口。

5. `SSH Login Username`是Daspire在连接到堡垒服务器时应该使用的用户名。这不是MySQL用户名。

6. 如果您使用`Password Authentication`，则`SSH Login Username`应设置为上一步用户的密码。如果您使用的是`SSH Key Authentication`，请将此留空。同样，这不是MySQL密码，而是Daspire用来在堡垒上执行命令的操作系统用户的密码。

7. 如果您使用`SSH Key Authentication`，则`SSH Private Key`应设置为您用于创建SSH连接的RSA私钥。这应该是以`-----BEGIN RSA PRIVATE KEY-----`开头并以`-----END RSA PRIVATE KEY-----`结尾的密钥文件的完整内容。