# Redshift

此页面包含Redshift的设置指南和参考信息。

## 前提条件

Daspire中的Redshift目的地有两种复制策略。Daspire会根据给定的配置自动选择一种方法——如果存在S3配置，Daspire将使用复制策略，反之亦然。

1. **INSERT：**通过SQL INSERT查询复制数据。它建立在目标jdbc代码库之上，并配置为依赖亚马逊通过Mulesoft[此处](https://mvnrepository.com/artifact/com.amazon.redshift/redshift-jdbc42)提供的JDBC 4.2标准驱动程序。如Redshift文档[此处](https://docs.aws.amazon.com/redshift/latest/mgmt/jdbc20-install.html)中所述。**不推荐用于生产环境负载，因为这不能很好地扩展**。

对于INSERT策略：

* **主机（Host）**
* **端口（Port）**
* **用户名**
* **密码**
* **架构**
* **数据库**
  * 该数据库需要存在于提供的集群中。
* **JDBC URL参数**（可选）

2. **复制：** 通过先将数据上传到S3存储桶并发出复制命令来复制数据。这是Redshift[最佳方式](https://docs.aws.amazon.com/redshift/latest/dg/c_loading-data-best-practices.html)描述的推荐加载方法。需要S3存储桶和凭据。

对于复制策略：

* **S3存储桶名称**
  * 请参阅[这里](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)创建S3存储桶。

* **S3桶区域**
  * 将S3存储桶和Redshift集群放在同一区域以节省网络成本。

* **访问密钥ID**
  * 请参阅[这里](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys)了解如何生成访问密钥。
  * 我们建议创建一个特定于Daspire的用户。此用户将需要[读取和写入权限](https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_examples_s3_rw-bucket.html)到临时存储桶中的对象。

* **秘密访问密钥**
  * 上面密钥id对应的密钥。

* **零件尺寸**
  * 影响单个Redshift表格的大小限制。可选的。如果同步表大于100GB，请增加此值。文件被分流到S3。这决定了每个部分的大小，以MB为单位。由于S3对每个文件有一万个零件的限制，零件大小会影响表格大小。默认情况下为10MB，导致默认表限制为100GB。请注意，较大的零件尺寸会导致较大的内存需求。一个经验法则是将部件大小乘以10以获得内存要求。小心修改这个。

* **S3文件名模式**
  * 该模式允许您设置S3暂存文件的文件名格式，当前支持下一个占位符组合：{date}、{date:yyyy\_MM}、{timestamp}、{timestamp:millis}、 {timestamp:micros}、{part\_number}、{sync\_id}、{format\_extension}。请不要使用空白区域和不支持的占位符，因为它们不会被识别。

可选参数：

* **桶路径**
  * S3存储桶中用于放置暂存数据的目录。例如，如果您将其设置为`yourFavoriteSubdirectory`，我们会将暂存数据放在`s3://yourBucket/yourFavoriteSubdirectory`中。如果未提供，则默认为根目录。

* **清除暂存数据**
  * 是否在完成同步后从S3中删除暂存文件。具体来说，接口将创建名为`bucketPath/namespace/streamName/syncDate_epochMillis_randomUuid.csv`的CSV文件，其中包含三列（`ab_id`、`data`、`emitted_at`）。通常这些文件在复制命令完成后被删除；如果您想保留它们用于其他目的，请将`purge_staging_data`设置为`false`。

## 设置指南

### 第1步：设置Redshift

1. [登录](https://aws.amazon.com/console/)到AWS管理控制台。如果您还没有AWS账户，则需要[创建](https://aws.amazon.com/premiumsupport/knowledge-center/create-and-activate-aws-account/)使用API。

2. 进入AWS Redshift服务

3. [创建](https://docs.aws.amazon.com/ses/latest/dg/event-publishing-redshift-cluster.html)并激活AWS Redshift集群（如果您还没有准备好的话）

4.（可选）[允许](https://aws.amazon.com/premiumsupport/knowledge-center/cannot-connect-redshift-cluster/)从Daspire连接到您的Redshift集群（如果它们存在于单独的VPC中）

5. （可选）[创建](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) 暂存 S3 存储桶（用于 COPY 策略）。

### 第2步：在Daspire中设置目的地接口

1. 进入Daspire控制面板。

2. 在左侧导航栏中，点击**目的地**。在右上角，点击**添加新目的地**。

3. 在目的地设置页面上，从目的地下拉列表中选择**Redshift**并输入此接口的名称。

4. 填写所有必填字段以使用插入或复制策略

5. 点击设置目的地。

## 支持的同步模式

Redshift目的地支持以下同步模式：

* 完全刷新同步
* 增量 - 追加同步
* 增量 - 去重历史

## 性能考虑

同步性能取决于要传输的数据量。集群扩展问题可以直接使用AWS Redshift控制台中的集群设置来解决。

## 特定目的地的特色和亮点

### 关于Redshift命名约定的注意事项

来自[Redshift名称和标识符](https://docs.aws.amazon.com/redshift/latest/dg/r_names.html)：

#### 标准标识符

* 以ASCII单字节字母字符或下划线字符开头，或以两到四个字节长的UTF-8多字节字符开头。

* 后续字符可以是ASCII单字节字母数字字符、下划线或美元符号，或者长度为两到四个字节的UTF-8多字节字符。

* 长度在1到127个字节之间，不包括分隔标识符的引号。

* 不包含引号和空格。

#### 分隔的标识符

分隔的标识符（也称为带引号的标识符）以双引号（"）开头和结尾。如果使用分隔的标识符，则必须为对该对象的每个引用使用双引号。标识符可以包含任何标准UTF-8双引号本身以外的可打印字符。因此，您可以创建包含其他非法字符（例如空格或百分号）的列名或表名。分隔的标识符中的ASCII字母不区分大小写并折叠为小写。要使用字符串中的双引号，您必须在它前面加上另一个双引号字符。

因此，Daspire Redshift目的地将尽可能使用不带引号的标识符创建表和方案，如果名称包含特殊字符，则回退到带引号的标识符。

### 数据大小限制

Redshift指定最大限制为1MB（JSON记录中的任何VARCHAR字段为65535字节）以存储原始JSON记录数据。因此，当一行太大而无法容纳时，Redshift，目的地无法加载此类数据并且当前会忽略该记录。请参阅[SUPER](https://docs.aws.amazon.com/redshift/latest/dg/r_SUPER_type.html) 和[SUPER 限制](https://docs.aws.amazon.com/redshift/latest/dg/limitations-super.html)的文档。

### 加密

所有Redshift链接都使用SSL加密。

## 输出模式

Daspire将每个数据流输出到Redshift中它自己的原始表中。每个表包含三列：

* `_daspire_ab_id`：Daspire分配给每个处理的事件的uuid。Redshift中的列类型是VARCHAR。

* `_daspire_emitted_at`：表示事件何时从数据源中提取的时间戳。Redshift中的列类型是TIMESTAMP WITH TIME ZONE。

* `_daspire_data`：用事件数据表示的json blob。Redshift中的列类型是VARCHAR，但可以使用JSON函数进行解析。

## 数据类型映射

| Daspire类型 | Redshift类型 |
| --- | --- |
| boolean | boolean |
| int | integer |
| float | number |
| varchar | string |
| date/varchar | date |
| time/varchar | time |
| timestamptz/varchar | timestamp\_with\_timezone |
| varchar | array |
| varchar | object |