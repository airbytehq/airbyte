# Snowflake

此页面包含Snowflake的设置指南和参考信息。

将Snowflake设置为目的地涉及在Snowflake控制面板中设置Snowflake实体（仓库、数据库、模式、用户和权限），设置数据加载方法（internal stage、AWS S3、Google Cloud Storage bucket或Azure Blob Storage），并在Daspire中配置Snowflake目的地。

此页面描述了将Snowflake设置为目的地的步骤。

## 前提条件

* 具有[ACCOUNTADMIN](https://docs.snowflake.com/en/user-guide/security-access-control-considerations.html)权限的Snowflake帐户。如果您没有具有ACCOUNTADMIN权限的帐户，请联系您的Snowflake管理员为您设置一个。

*（可选）AWS、Google Cloud Storage或Azure帐户。

## 网络政策

默认情况下，Snowflake允许用户从任何计算机或设备IP地址连接到该服务。安全管理员（即具有SECURITYADMIN权限的用户）或更高级别的管理员可以创建网络策略以允许或拒绝访问单个IP地址或地址列表。

如果您在连接Daspire时遇到任何问题，请确保IP地址列表在允许列表中。

要确定是否为您的帐户或特定用户设置了网络政策，请执行SHOW PARAMETERS命令。

**账户**
```SHOW PARAMETERS LIKE 'network_policy' IN ACCOUNT;```

**用户**
```SHOW PARAMETERS LIKE 'network_policy' IN USER <username>;```

要了解更多信息，请查看官方[Snowflake文档](https://docs.snowflake.com/en/user-guide/network-policies.html#)

## 设置指南

### 第1步：在Snowflake中设置特定于Daspire的实体

要设置Snowflake目标连接器，您首先需要创建特定于Daspire的Snowflake实体（仓库、数据库、架构、用户和权限），并具有OWNERSHIP权限以将数据写入Snowflake、跟踪与Daspire相关的成本并控制权限在粒度级别。

您可以在新的[Snowflake worksheet](https://docs.snowflake.com/en/user-guide/ui-worksheet.html)中使用以下脚本来创建实体：

1. [登录您的Snowflake帐户](https://www.snowflake.com/login/)。

2. 编辑以下脚本，将密码更改为更安全的密码，并根据需要更改其他资源的名称。

  > **注意：**确保在重命名资源时遵循[Snowflake标识符要求](https://docs.snowflake.com/en/sql-reference/identifiers-syntax.html)。

```
 set variables (these need to be uppercase)
 set daspire_role = 'DASPIRE_ROLE';
 set daspire_username = 'DASPIRE_USER';
 set daspire_warehouse = 'DASPIRE_WAREHOUSE';
 set daspire_database = 'DASPIRE_DATABASE';
 set daspire_schema = 'DASPIRE_SCHEMA';

 -- set user password
 set daspire_password = 'password';

 begin;

 -- create Daspire role
 use role securityadmin;
 create role if not exists identifier($daspire_role);
 grant role identifier($daspire_role) to role SYSADMIN;

 -- create Daspire user
 create user if not exists identifier($daspire_username)
 password = $daspire_password
 default_role = $daspire_role
 default_warehouse = $daspire_warehouse;

 grant role identifier($daspire_role) to user identifier($daspire_username);

 -- change role to sysadmin for warehouse / database steps
 use role sysadmin;

 -- create Daspire warehouse
 create warehouse if not exists identifier($daspire_warehouse)
 warehouse_size = xsmall
 warehouse_type = standard
 auto_suspend = 60
 auto_resume = true
 initially_suspended = true;

 -- create Daspire database
 create database if not exists identifier($daspire_database);

 -- grant Daspire warehouse access
 grant USAGE
 on warehouse identifier($daspire_warehouse)
 to role identifier($daspire_role);

 -- grant Daspire database access
 grant OWNERSHIP
 on database identifier($daspire_database)
 to role identifier($daspire_role);

 commit;

 begin;

 USE DATABASE identifier($daspire_database);

 -- create schema for Daspire data
 CREATE SCHEMA IF NOT EXISTS identifier($daspire_schema);

 commit;

 begin;

 -- grant Daspire schema access
 grant OWNERSHIP
 on schema identifier($daspire_schema)
 to role identifier($daspire_role);

 commit;
```

3. 使用 [Worksheet page](https://docs.snowflake.com/en/user-guide/ui-worksheet.html)或[Snowlight](https://docs.snowflake.com/en/user-guide/ui-snowsight-gs.html)运行脚本。确保选中**All Queries**勾选框。

### 第二步：设置数据加载方式

默认情况下，Daspire使用Snowflake的[Internal Stage](https://docs.snowflake.com/en/user-guide/data-load-local-file-system-create-stage.html)加载数据。您还可以使用 [Amazon S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)、[Google Cloud Storage bucket](https://cloud. google.com/storage/docs/introduction）或[Azure Blob Storage](https://docs.microsoft.com/en-us/azure/storage/blobs/)。

确保数据库和模式具有USAGE权限。

#### 使用Amazon S3 bucket

要使用Amazon S3 bucket，[创建一个新的Amazon S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html)，具有Daspire的读/写访问权限将数据暂存到Snowflake。

#### 使用Google Cloud Storage bucket

要使用Google Cloud Storage bucket：

1. 导航到Google Cloud Console并[创建一个新的存储桶](https://cloud.google.com/storage/docs/creating-buckets)，为Daspire提供读/写访问权限以将数据暂存到Snowflake。

2. 为您的服务帐户[生成JSON密钥](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating_service_account_keys)。

3. 编辑以下脚本，将DASPIRE\_ROLE替换为您用于Daspire的Snowflake配置的角色，并将YOURBUCKETNAME替换为您的存储桶名称。

```
 create storage INTEGRATION gcs_daspire_integration
 TYPE = EXTERNAL_STAGE
 STORAGE_PROVIDER = GCS
 ENABLED = TRUE
 STORAGE_ALLOWED_LOCATIONS = ('gcs://YOURBUCKETNAME');

 create stage gcs_daspire_stage
 url = 'gcs://YOURBUCKETNAME'
 storage_integration = gcs_daspire_integration;

 GRANT USAGE ON integration gcs_daspire_integration TO ROLE DASPIRE_ROLE;
 GRANT USAGE ON stage gcs_daspire_stage TO ROLE DASPIRE_ROLE;

 DESC STORAGE INTEGRATION gcs_daspire_integration;
```

4. 最终查询应显示带有电子邮件作为属性值的`STORAGE_GCP_SERVICE_ACCOUNT`属性。使用该电子邮件向您的存储桶添加读/写权限。

5. 导航到Snowflake控制面板并使用[Worksheet page ](https://docs.snowflake.com/en/user-guide/ui-worksheet.html)或[Snowlight](https://docs.snowflake.com/en/user-guide/ui-snowsight-gs.html）。

#### 使用Azure Blob Storage

要使用Azure Blob Storage，[创建存储帐户](https://docs.microsoft.com/en-us/azure/storage/common/storage-account-create?tabs=azure-portal)和[容器]( https://docs.microsoft.com/en-us/rest/api/storageservices/create-container)，并提供一个[SAS Token](https://docs.snowflake.com/en/user-guide/data -load-azure-config.html#option-2-generating-a-sas-token)访问容器。我们建议为Daspire创建一个专用容器，以将数据暂存到Snowflake。Daspire需要读/写权限才能与此容器交互。

### 第3步：在Daspire中将Snowflake设置为目的地

导航到Daspire以将Snowflake设置为目的地。您可以使用用户名/密码或OAuth 2.0进行身份验证：

#### 用户名和密码

| 字段 | 说明 |
| --- | --- |
| 主机（Host） | Snowflake实例的主机域名（必须包含账号、地域、云环境，以snowflakecomputing.com结尾）。示例：accountname.us-east-2.aws.snowflakecomputing.com |
| 权限（Role） | 您在第1步中为Daspire创建的用于访问Snowflake的角色。示例：DASPIRE\_ROLE |
| 仓库（Warehouse） | 您在第1步中为Daspire创建的用于同步数据的仓库。示例：DASPIRE\_WAREHOUSE |
| 数据库（Database） | 您在步骤1中为Daspire将数据同步到其中创建的数据库。示例：DASPIRE\_DATABASE |
| 模式（Schema） | 默认模式用作从链接发出的所有未明确指定模式名称的语句的目标模式 |
| 用户名 | 您在第1步中创建的用户名，以允许Daspire访问数据库。示例：DASPIRE\_USER |
| 密码 | 与用户名关联的密码 |
| JDBC URL参数（可选）| 连接到数据库时要传递给JDBC URL字符串的附加属性，格式为由符号&分隔的键=值（key=value）对。示例：key1=value1&key2=value2&key3=value3 |

#### OAuth 2.0

| 字段 | 说明 |
| --- | --- |
| 主机（Host） | Snowflake实例的主机域名（必须包含账号、地域、云环境，以snowflakecomputing.com结尾）。示例：accountname.us-east-2.aws.snowflakecomputing.com |
| 权限（Role） | 您在第1步中为Daspire创建的用于访问Snowflake的角色。示例：DASPIRE\_ROLE |
| 仓库（Warehouse） | 您在第1步中为Daspire创建的用于同步数据的仓库。示例：DASPIRE\_WAREHOUSE |
| 数据库（Database） | 您在步骤1中为Daspire将数据同步到其中创建的数据库。示例：DASPIRE\_DATABASE |
| 模式（Schema） | 默认模式用作从链接发出的所有未明确指定模式名称的语句的目标模式 |
| 用户名 | 您在第1步中创建的用户名，以允许Daspire访问数据库。示例：DASPIRE\_USER |
| OAuth2 | 用于获取身份验证令牌的登录名和密码 |
| JDBC URL参数（可选） | 连接到数据库时要传递给JDBC URL字符串的附加属性，格式为由符号&分隔的键=值（key=value）对。示例：key1=value1&key2=value2&key3=value3 |

#### 密钥对认证

```
 In order to configure key pair authentication you will need a private/public key pair.
 If you do not have the key pair yet, you can generate one using openssl command line tool
 Use this command in order to generate an unencrypted private key file:

 `openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out rsa_key.p8 -nocrypt`

 Alternatively, use this command to generate an encrypted private key file:

 `openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -v1 PBE-SHA1-RC4-128 -out rsa_key.p8`

 Once you have your private key, you need to generate a matching public key.
 You can do so with the following command:

 `openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub`

 Finally, you need to add the public key to your Snowflake user account.
 You can do so with the following SQL command in Snowflake:

 `alter user <user_name> set rsa_public_key=<public_key_value>;`

 and replace <user_name> with your user name and <public_key_value> with your public key. 
```

要使用**AWS S3**作为云存储，请输入您在第2步中创建的S3 bucket的信息：

| 字段 | 说明 |
| --- | --- |
| S3存储桶名称 | Staging S3存储桶的名称（示例：daspire.staging）。Daspire会将文件写入此存储桶并通过Snowflake上的语句读取它们。 |
| S3桶区域 | 使用的S3暂存桶区域。 |
| S3 Key ID \* | 授予对S3暂存存储桶的访问权限的访问密钥ID。Daspire需要存储桶的读取和写入权限。 |
| S3 Access Key \* | S3 Key ID的相应秘密。 |
| 流部分大小（可选）| 如果同步表大于100GB，请增加此值。文件被分流到S3。这决定了每个部分的大小，以MB为单位。由于S3对每个文件有一万个零件的限制，零件大小会影响表格大小。默认情况下为10MB，因此表的默认限制为100GB。请注意，较大的零件尺寸会导致较大的内存需求。一个常见的做法是将部件大小乘以10以获得内存要求。小心修改这个。（例如5） |
| 清除暂存文件和表 | 确定是否在完成同步后从S3中删除暂存文件。具体来说，链接将创建名为bucketPath/namespace/streamName/syncDate\_epochMillis\_randomUuid.csv的CSV文件，其中包含三列（ab\_id、data、emitted\_at）。通常这些文件在同步后会被删除；如果您想保留它们用于其他目的，请将 purge\_staging\_data设置为false。 |
| 加密 | S3上的文件是否加密。您可能不需要启用此功能，但如果您与其他应用程序共享数据存储，它可以提供额外的安全层。如果您确实使用加密，则必须在临时密钥（Daspire会为每次同步自动生成一个新密钥，只有Daspire和Snowflake能够读取S3上的数据）或提供您自己的密钥（如果您有 “清除暂存文件和表（Purge staging files and tables）”选项已禁用，并且您希望能够自己解密数据）|
| S3文件名模式（可选）| 该模式允许您为S3暂存文件设置文件名格式，当前支持下一个占位符组合：{date}、{date:yyyy\_MM}、{timestamp}、{timestamp:millis}、{ timestamp:micros}、{part\_number}、{sync\_id}、{format\_extension}。请不要使用空白区域和不支持的占位符，因为它们不会被识别。 |

要使用**Google Cloud Storage**存储桶，请输入您在第2步中创建的存储桶的信息：

| 字段 | 说明 |
| --- | --- |
| GCP项目ID | 您的凭据的GCP项目ID的名称。（例如：my-project）|
| GCP存储桶名称 | 暂存桶的名称。Daspire会将文件写入此存储桶并通过Snowflake上的语句读取它们。（例如：daspire-staging）|
| 谷歌应用凭证 | 对暂存GCS存储桶具有读/写权限的JSON密钥文件的内容。您将需要单独授予对您的Snowflake GCP服务帐户的存储桶访问权限。有关如何为您的服务帐户生成JSON密钥的更多信息，请参阅Google Cloud文档。 |

要使用**Azure Blob**存储，请输入您在第2步中创建的存储的信息：

| 字段 | 说明 |
| --- | --- |
| 端点域名 | 保留默认值blob.core.windows.net或将自定义域映射到Azure Blob存储终结点。 |
| Azure Blob存储帐户名称 | 您在步骤2中创建的Azure存储帐户。
| Azure blob存储容器（Bucket）名称 | 您在步骤2中创建的Azure blob存储容器。
| SAS Token | 您在步骤2中提供的SAS令牌。

## 输出模式

Daspire将每个数据流输出到它自己的表中，在Snowflake中具有以下列：

| Daspire字段 | 说明 | 列类型 |
| --- | --- | --- |
| \_daspire\_ab\_id | 分配给每个已处理事件的UUID | VARCHAR |
| \_daspire\_emitted\_at | 从数据源中提取事件的时间戳 | 带时区的时间戳 |
| \_daspire\_data | 包含事件数据的JSON blob | VARIANT |

**注意：** 默认情况下，Daspire创建永久表。如果您更倾向于临时表，请为Daspire创建一个专用的临时数据库。有关更多信息，请参阅[Working with Temporary and Transient Tables](https://docs.snowflake.com/en/user-guide/tables-temp-transient.html)。

## 支持的同步模式

Snowflake目的地支持以下同步模式：

* 完全刷新同步 - 覆盖
* 完全刷新同步 - 追加
* 增量同步 - 追加
* 增量同步 - 去重历史