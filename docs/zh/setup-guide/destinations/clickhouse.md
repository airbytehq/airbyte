# ClickHouse

## 前提条件

### 服务器

ClickHouse服务器版本21.8.10.19或更高版本

### 配置网络访问

确保您的ClickHouse数据库可以被Daspire访问。如果您的数据库位于VPC内，您可能需要允许从您用于公开Daspire的IP进行访问。

### 权限

您需要具有以下权限的ClickHouse用户：

* 可以创建表和写入行
* 可以创建数据库，例如：

您可以通过运行以下命令来创建这样的用户：

```
GRANT CREATE ON * TO daspire_user；
```

您也可以使用已存在的用户，但我们强烈建议为Daspire创建一个专用用户。

### 目标数据库

您将需要选择一个现有数据库或创建一个新数据库，用于存储来自Daspire的同步数据。

## 功能

| 功能 | 是否支持 |
| --- | --- |
| 完全刷新同步 | 是 |
| 增量 - 追加同步 | 是 |
| 增量 - 去重历史 | 是 |
| 命名空间 | 是 |

### 输出模式

每个数据流都将输出到ClickHouse它自己的表中。每个表包含3列：

* `_daspire_ab_id`：Daspire分配给每个处理的事件的uuid。ClickHouse中的列类型是`String`。

* `_daspire_emitted_at`：表示事件何时从数据源中提取的时间戳。ClickHouse中的列类型是`DateTime64`。

* `_daspire_data`：表示事件数据的json blob。ClickHouse中的列类型是`String`。

## 设置指南

您现在应该具备将ClickHouse配置为目的的所需的所有要求。您需要以下信息来配置ClickHouse目的地：

* **主机**
* **端口**
* **用户名**
* **密码**
* **数据库**
* **Jdbc\_url\_params**

### 命名约定

来自[ClickHouse SQL标识符语义](https://clickhouse.com/docs/en/sql-reference/syntax/)：

* SQL标识符和关键字必须以字母（a-z，以及带变音符号和非拉丁字母的字母）或下划线（\_）开头。

* 标识符或关键字中的后续字符可以是字母、下划线或数字（0-9）。

* 标识符可以被引用或不被引用。建议不引用。

* 如果要使用与关键字相同的标识符，或者要在标识符中使用其他符号，请使用双引号或反引号将其引用，例如`id`。

* 如果您想编写可移植的应用程序，建议引用一个特定的名字或者永远不要引用它。

Daspire ClickHouse目的地将尽可能使用不带引号的标识符创建表和模式，如果名称包含特殊字符，则回退到带引号的标识符。