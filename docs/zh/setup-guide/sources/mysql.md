# MySQL

此页面包含MySQL的设置指南和参考信息。

## 前提条件

* MySQL服务器`8.0`、`5.7`或`5.6`。
* 创建一个专用的只读Daspire用户，可以访问复制所需的所有表。
* 主机
* 端口
* 数据库
* 用户名
* 密码

## 功能

| 功能 | 是否支持 | 备注 |
| --- | --- | --- |
| 完全更新 | 支持 |
| 增量更新 - 追加同步 | 支持 |
| 复制增量删除 | 支持 |
| CDC | 支持 |
| SSL支持 | 支持 |
| SSH通道连接 | 支持 |
| 命名空间 | 支持 | 默认启用 |
| 数组 | 支持 | 尚不支持字节数组 |

MySQL源代码不会改变数据库中的模式。但是，根据连接到此数据源的目的地，架构可能会更改。更详细信息，请参阅目的地的文档。

## 设置指南

**1. 确保您的数据库可以从运行Daspire的机器上访问**

这取决于您的网络设置。验证Daspire是否能够连接到您的MySQL最简单方法是通过用户界面中的检查连接工具。

**2. 创建一个可以访问相关表的专用只读用户（推荐但可选）**

此步骤是可选的，但我们强烈建议您不要跳过以更好的控制权限和审核。或者，您可以将Daspire与数据库中的现有用户一起使用。

要创建专用数据库用户，您可以在数据库运行以下命令：

```
CREATE USER 'daspire'@'%' IDENTIFIED BY 'your_password_here'; 
```

`标准（STANDARD）`和`变更数据捕获（CDC）`复制方法之间的正确权限集不同。对于`标准（STANDARD）`复制方法，只需要`选择（SELECT）`权限。

```
GRANT SELECT ON <database name>.* TO 'daspire'@'%';
``` 

对于`变更数据捕获（CDC）`复制方法，需要`选择（SELECT）`、`重新加载（RELOAD）`、`显示数据库（SHOW DATABASES）`、`复制从站（REPLICATION SLAVE）`、`复制客户端（REPLICATION CLIENT）`权限。

```
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'daspire'@'%'; 
```

**3. 设置CDC**

这不适用于`标准（STANDARD）`复制方式。这个选项是必选的如果您选择`变更数据捕获（CDC）`复制方法。请阅读下面的[变更数据捕获（CDC）部分](#change-data-capture-cdc)了解更多。

**4. 设置完成**

您的数据库用户现在应该可以使用Daspire了。

## 变更数据捕获（CDC）

* 如果您需要删除记录并且可以接受下面发布的限制，您应该可以使用MySQL的CDC。

* 如果您的数据集很小，并且您只想要目标中表的快照，请考虑对您的表使用完全刷新复制而不是CDC。

* 如果有限制阻止您使用CDC，并且您的目标是在目标中维护表的快照，请考虑使用非CDC增量并偶尔重置数据并重新同步。

* 如果您的表有一个主键但没有用于增量同步的合理游标字段（即`updated_at`）CDC允许您以增量方式同步您的表。

### 变更数据捕获（CDC）限制

* CDC增量仅支持具有主键的表。CDC源仍然可以选择复制没有主键的表作为完全刷新，或者可以为同一数据库配置非CDC源以使用标准增量复制复制没有主键的表。

* 数据必须在表中，而不是视图中。

* 您尝试捕获的修改必须使用`DELETE`/`INSERT`/`UPDATE`进行。例如，从`TRUNCATE`/`ALTER`所做的更改不会出现在日志中，因此不会出现在您的目标中。

* 我们不支持自动更改CDC源的架构。如果您更改架构，我们建议您重置并重新同步数据。

* 存在特定于数据库的限制。有关详细信息，请参阅各个接口的文档页面。

* `DELETE`语句产生的记录只包含主键。所有其他数据字段均未设置。

* 我们的CDC实施对所有变更记录使用至少一次交付。

#### 1. 启用二进制日志记录

您必须为MySQL复制启用二进制日志记录。二进制日志记录事务更新，供复制工具传播更改。您可以使用以下属性配置MySQL服务器配置文件，如下所述：

```
server-id                  = 223344
log_bin                    = mysql-bin
binlog_format              = ROW
binlog_row_image           = FULL
binlog_expire_log_seconds  = 864000
```

* `server-id`：对于MySQL集群中的每个服务器和复制客户端，server-id的值必须是唯一的。`server-id`应该是一个非零值。如果`server-id`已设置为非零值，则无需进行任何更改。您可以将`server-id`设置为1到4294967295之间的任何值。有关更多信息，请参阅[MySQL文档](https://dev.mysql.com/doc/refman/8.0/en/replication-options.html#sysvar_server_id）。

* `log_bin`：`log_bin`的值是binlog文件序列的基本名称。如果`log_bin`已经设置，则无需进行任何更改。有关详细信息，请参阅[MySQL文档](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#option_mysqld_log-bin)。

* `binlog_format`：`binlog_format`必须设置为`ROW`。有关详细信息，请参阅 [MySQL文档](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_binlog_format)。

* `binlog_row_image`：`binlog_row_image`必须设置为`FULL`。它确定如何将行图像写入二进制日志。有关详细信息，请参阅 [MySQL文档](https://dev.mysql.com/doc/refman/5.7/en/replication-options-binary-log.html#sysvar_binlog_row_image)。

* `binlog_expire_log_seconds`：这是自动清除binlog文件的秒数。我们建议864000秒（10天），以便在同步失败或同步暂停的情况下，我们仍然有一些带宽可以从增量同步的最后一个点开始。我们还建议为CDC设置频繁同步。

#### 2. 启用全球交易标识符（GTID）（可选）

全球交易标识符（GTID）唯一标识集群内服务器上发生的事务。虽然Daspire MySQL设置不需要，但使用GTID可以简化复制并使您能够更轻松地确认主服务器和副本服务器是否一致。有关详细信息，请参阅 [MySQL文档](https://dev.mysql.com/doc/refman/8.0/en/replication-options-gtids.html#option_mysqld_gtid-mode)。

* 启用`gtid_mode`：布尔值，指定是否启用MySQL服务器的GTID模式。通过`mysql> gtid_mode=ON`启用它

* 启用`enforce_gtid_consistency`：指定服务器是否通过允许执行可以事务安全方式记录的语句来强制执行GTID一致性的布尔值。使用GTID时需要。通过`mysql> enforce_gtid_consistency=ON`启用它

**笔记**

当第一次使用CDC运行同步时，Daspire会执行数据库的初始一致快照。Daspire在创建快照以允许其他数据库客户端写入时不获取任何表锁（对于使用MyISAM引擎定义的表，表仍将被锁定）。但是为了使同步工作没有任何错误/意外行为，假设在快照运行时没有发生架构更改。

## 通过SSH隧道连接

Daspire能够通过SSH隧道连接到MySQL实例。您可能想要这样做的原因是不可能（或违反安全策略）直接连接到数据库（例如，它没有公共IP地址）。

使用SSH隧道时，您正在配置Daspire以连接到可以直接访问数据库的中间服务器（也称为堡垒服务器）。Daspire连接到堡垒，然后要求堡垒直接连接到服务器。

使用此功能需要在创建源时进行额外配置。我们将讨论每个配置的含义。

1. 像往常一样配置源的所有字段，`SSH Tunnel Method`除外。

2. `SSH Tunnel Method`默认为`No Tunnel`（即直接连接）。如果您想使用SSH隧道，请选择`SSH Key Authentication`或`Password Authentication`。

  * 如果您将使用RSA私钥作为建立SSH隧道的秘密，请选择`Key Authentication`（有关生成此密钥的更多信息，请参见下文）。

  * 如果您将使用密码作为建立SSH隧道的秘密，请选择`Password Authentication`。

3. `SSH Tunnel Jump Server Host`是指Daspire将要连接的中间（堡垒）服务器。这应该是主机名或IP地址。

4. `SSH Connection Port`是堡垒服务器上建立SSH连接的端口。SSH连接的默认端口是`22`，因此除非您明确更改了某些内容，否则请使用默认端口。

5. `SSH Login Username`是Daspire在连接到堡垒服务器时应该使用的用户名。这不是MySQL用户名。

6. 如果您使用`Password Authentication`，则`SSH Login Username`应设置为上一步用户的密码。如果您使用的是`SSH Key Authentication`，请将此留空。同样，这不是MySQL密码，而是Daspire用来在堡垒上执行命令的操作系统用户的密码。

7. 如果您使用`SSH Key Authentication`，则`SSH Private Key`应设置为您用于创建SSH连接的RSA私钥。这应该是以`-----BEGIN RSA PRIVATE KEY-----`开头并以`-----END RSA PRIVATE KEY-----`结尾的密钥文件的完整内容。

### 生成SSH密钥对

连接器需要PEM格式的RSA密钥。要生成此密钥：

```
ssh-keygen -t rsa -m PEM -f myuser_rsa
```

这会生成pem格式的私钥，而公钥保留为堡垒主机上的`authorized_keys`文件使用的标准格式。应将公钥添加到您的堡垒主机，以供您希望与Daspire一起使用的任何用户使用。私钥通过复制并粘贴到Daspire连接配置屏幕提供，因此它可以登录堡垒。

## 数据类型映射

| MySQL类型 | Daspire类型 | 备注 |
| --- | --- | --- |
| `bit(1)` | boolean |
| `bit(\>1)` | base64 binary string |
| `boolean` | boolean |
| `tinyint(1)` | boolean |
| `tinyint(\>1)` | boolean |
| `smallint` | number |
| `mediumint` | number |
| `int` | number |
| `bigint` | number |
| `float` | number |
| `double` | number |
| `decimal` | number |
| `binary` | string |
| `blob` | string |
| `date` | string | ISO 8601日期字符串。ZERO-DATE值将转换为NULL。如果列是必需的，则转换为EPOCH。 |
| `datetime`, `timestamp` | string | ISO 8601日期字符串。ZERO-DATE值将转换为NULL。如果列是必需的，则转换为EPOCH。 |
| `time` | string | ISO 8601时间字符串。值介于00:00:00和23:59:59之间。 |
| `year` | year string | [Doc](https://dev.mysql.com/doc/refman/8.0/en/year.html) |
| `char`, `varchar` with non-binary charset | string |
| `char`, `varchar` with binary charset | base64 binary string |
| `tinyblob` | base64 binary string |
| `blob` | base64 binary string |
| `mediumblob` | base64 binary string |
| `longblob` | base64 binary string |
| `binary` | base64 binary string |
| `varbinary` | base64 binary string |
| `tinytext` | string |
| `text` | string |
| `mediumtext` | string |
| `longtext` | string |
| `json` | serialized json string | E.g. {"a": 10, "b": 15} |
| `enum` | string |
| `set` | string | E.g. blue,green,yellow |
| `geometry` | base64 binary string |

注意：如果您没有在此列表中看到类型，则可认为它已被强制转换为字符串。

## 故障排除

将MySQL的日期时间字段中的值映射到其他关系数据存储可能会出现问题。MySQL允许日期/时间为零值，而不是其他数据存储可能不接受的NULL。要解决此问题，您可以在源设置`zerodatetimebehavior=Converttonull`的JDBC接口中传递以下键值对。

一些用户报告说他们无法连接到Amazon RDS MySQL或MariaDB。这可以通过错误消息进行诊断：`Cannot create a PoolableConnectionFactory`。要解决此问题，请在JDBC参数中添加enabledTLSProtocols=TLSv1.2。

用户在尝试连接到Amazon RDS MySQL时报告的另一个错误是`Error: HikariPool-1 - Connection is not available, request timed out after 30001ms.`。很多时候这可能是由于VPC不允许公共流量。但是，我们建议查看[此AWS故障排除清单]（https://aws.amazon.com/premiumsupport/knowledge-center/rds-cannot-connect/）以确保已授予正确的权限/设置以允许连接到您的数据库。