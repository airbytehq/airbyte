# BigQuery

此页面包含BigQuery的设置指南和参考信息。

设置BigQuery目的地包括设置数据加载方法（BigQuery标准方法和Google Cloud Storage (GCS) 存储桶）和使用Daspire配置BigQuery目的地接口。

## 前提条件

* [启用了BigQuery的谷歌云项目](https://cloud.google.com/bigquery/docs/quickstarts/query-public-dataset-console)
* [BigQuery数据集](https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui#create_a_dataset)以同步数据至数据集

  > **注意：**用BigQuery编写的查询只能引用同一物理位置的数据集。如果您计划将Daspire同步的数据与查询中其他数据集的数据相结合，请在谷歌云上的相同位置创建数据集。有关详细信息，请阅读[数据集简介](https://cloud.google.com/bigquery/docs/datasets-intro)

* 具有[BigQuery用户（User）](https://cloud.google.com/bigquery/docs/access- control#bigquery)和[BigQuery数据编辑器（Data Editor）](https://cloud.google.com/bigquery/docs/access-control#bigquery)角色和[JSON格式的服务帐户密钥（ServiceAccountKey）](https://cloud.google.com/iam/docs/creating-managing-service-account-keys）。

## 链接模式

在设置BigQuery时，您可以将其配置为以下模式：

* **BigQuery**：通过将JSON blob数据存储在\_daspire\_raw\_\*表格中，然后将数据转换和规范化到单独的表中来生成数据正常化输出，如果基本规范化是，可能会将嵌套流分解到它们自己的表中配置。

* **BigQuery（非规范化）**：利用具有结构化和重复字段的BigQuery功能为每个数据流生成一个“大”表。Daspire目前不支持此选项的数据正常化。

## 设置指南

### 第一步：设置数据加载方式

虽然您可以使用BigQuery的[INSERTS](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax)加载数据，但我们强烈建议您使用[谷歌云存储桶（Google Cloud Storage bucket）](https://cloud.google.com/storage/docs/introduction）。

#### 使用谷歌云存储桶（推荐）

使用谷歌云存储桶（Google Cloud Storage bucket）：

1. [创建谷歌云存储桶（Cloud Storage bucket）](https://cloud.google.com/storage/docs/creating-buckets)，将保护工具设置为无或对象版本控制。确保存储桶没有[保留策略（retention policy）](https://cloud.google.com/storage/docs/samples/storage-set-retention-policy)。

2. [创建HMAC密钥（HMAC key）和访问ID（access ID）](https://cloud.google.com/storage/docs/authentication/managing-hmackeys#create)。

3. 授予[存储对象管理员（Storage Object Admin）](https://cloud.google.com/storage/docs/access-control/iam-roles#standard-roles)[权限（role）](https://cloud.google.com/ storage/docs/access-control/iam-roles#standard-roles)到谷歌云[服务帐户（Service Account）](https://cloud.google.com/iam/docs/service-accounts)。

4. 确保可以从运行Daspire的机器访问您的云存储存储桶。验证Daspire是否能够连接到您的存储桶的最简单方法是通过控制面板中的检查连接工具。

#### 使用`INSERT`

您可以使用BigQuery的[INSERT](https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax)语句将数据直接从数据源上传到BigQuery。虽然最初设置起来更快，但我们强烈建议不要将此选项用于快速演示以外的任何用途。由于谷歌BigQuery SDK客户端限制，使用INSERT比使用谷歌云存储存储桶慢10倍，并且您可能会看到大数据集和慢速源的一些失败（例如，如果从数据源读取需要超过10-12小时).

### 第2步：在Daspire中设置BigQuery目的地

1. 登录您的Daspire帐户。

2. 点击**目的地**，然后点击**添加新目的地**。

3. 在设置目标页面上，从**目的地**下拉列表中选择**BigQuery**或**BigQuery（非正常化类型结构）**，具体取决于您是要在BigQuery还是BigQuery非正常化类型结构中进行设置。

4. 输入BigQuery链接的名称。

5. 对于**项目ID**，输入您的[谷歌云项目ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects)。

6. 对于**数据集位置**，选择您的BigQuery数据集的位置。

  **注意：**您以后无法更改位置。

7. 对于**默认数据集ID**，输入BigQuery[数据集ID](https://cloud.google.com/bigquery/docs/datasets#create-dataset)。

8. 对于**加载方式**，选择标准插入（Standard Inserts）或谷歌云存储暂存（GCS Staging）。

  **提示：**我们建议使用谷歌云存储暂存选项。

9. 对于**服务帐户密钥JSON（云端必需，开源可选）**，输入谷歌云[JSON格式的服务帐户密钥](https://cloud.google.com/iam/docs/creating-managing-service-account-keys）。

10. 对于**转换查询运行类型（可选）**，选择**交互**以让[BigQuery运行交互式查询作业](https://cloud.google.com/bigquery/docs/running-queries#queries ) 或**批量**让[BigQuery运行批量查询](https://cloud.google.com/bigquery/docs/running-queries#batch)。

  **注意：**交互式查询会尽快执行并计入每日并发配额和限制，而批量查询会在BigQuery共享资源池中有可用资源时立即执行。如果BigQuery未在24小时内开始查询BigQuery会将作业优先级更改为交互式。批量查询不计入您的并发速率限制，这样可以更轻松地同时启动多个查询。

11. 对于**谷歌BigQuery客户端块大小（可选）**，使用默认值15 MiB。稍后，如果您发现同步出现网络或内存管理问题（特别是在目的地上），请尝试减小块大小。在这种情况下，同步会更慢但更有可能成功。

## 支持的同步模式

BigQuery目的地支持以下同步模式：

* 完全刷新同步
* 增量 - 追加同步
* 增量 - 去重历史

## 输出模式

Daspire将每个数据流输出到BigQuery中它自己的表中。每个表包含三列：

* `_daspire_ab_id`：Daspire分配给每个处理的事件的UUID。BigQuery中的列类型是字符串。

* `_daspire_emitted_at`：表示事件何时从数据源中提取的时间戳。BigQuery中的列类型是时间戳。

* `_daspire_data`：表示事件数据的JSON blob。BigQuery中的列类型是字符串。

BigQuery中的输出表按时间单位列`_daspire_emitted_at`以每日粒度进行分区和聚类。分区边界基于格林威治标准时间。通过使用谓词过滤器（WHERE子句），这对于在查询这些分区表时限制扫描的分区数很有用。分区列上的过滤器用于修剪分区并降低查询成本。（Daspire未启用参数**必需分区过滤器**，但您可以通过更新生成的表来切换它。）

## BigQuery命名约定

遵循[BigQuery数据集命名约定](https://cloud.google.com/bigquery/docs/datasets#dataset-naming)。

Daspire在写入数据时将任何无效字符转换为`_`字符。但是，由于以`_`开头的数据集隐藏在BigQuery Explorer控制面板上，因此Daspire会在命名空间前加上n以表示转换后的命名空间。

## 数据类型映射

| Daspire类型 | BigQuery类型 | BigQuery非规范化类型 |
| --- | --- | --- |
| DATE | DATE | DATE |
| STRING (BASE64) | STRING | STRING |
| NUMBER | FLOAT | FLOAT |
| OBJECT | STRING | RECORD |
| STRING | STRING | STRING |
| BOOLEAN | BOOLEAN | BOOLEAN |
| INTEGER | INTEGER | INTEGER |
| STRING (BIG\_NUMBER) | STRING | STRING |
| STRING (BIG\_INTEGER) | STRING | STRING |
| ARRAY | REPEATED | REPEATED |
| STRING (TIMESTAMP\_WITH\_TIMEZONE) | TIMESTAMP | DATETIME |
| STRING (TIMESTAMP\_WITHOUT\_TIMEZONE) | TIMESTAMP | DATETIME |

## 解决权限问题

服务帐户没有适当的权限：

* 确保BigQuery服务帐户具有BigQuery User和BigQuery Data Editor权限或与这两个权限等效的权限。

* 如果选择谷歌云存储暂存模式，请确保BigQuery服务帐户对谷歌云存储存储桶和路径或云存储管理员权限具有正确的权限，其中包括所需权限的超集。

HMAC密钥错误：

* 确保为BigQuery服务帐户创建了HMAC密钥，并且该服务帐户有权访问谷歌云存储存储桶和路径。