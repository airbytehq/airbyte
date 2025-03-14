# MSSQL

## Features

| Feature                        | Supported?\(Yes/No\) | Notes |
| :----------------------------- | :------------------- | :---- |
| Full Refresh Sync              | Yes                  |       |
| Incremental - Append Sync      | Yes                  |       |
| Incremental - Append + Deduped | Yes                  |       |
| Namespaces                     | Yes                  |       |

## Output Schema

Each stream will be output into its own table in SQL Server. Each table will contain the following metadata columns:

- `_airbyte_raw_id`: A random UUID assigned to each incoming record. The column type in SQL Server is `VARCHAR(MAX)`.
- `_airbyte_extracted_at`: A timestamp for when the event was pulled from the data source. The column type in SQL Server is `BIGINT`.
- `_airbyte_meta`: Additional information about the record. The column type in SQL Server is `TEXT`.
- `_airbyte_generation_id`: Incremented each time a [refresh](https://docs.airbyte.com/operator-guides/refreshes) is executed.  The column type in SQL Server is `TEXT`.

See [here](../../understanding-airbyte/airbyte-metadata-fields) for more information about these fields.

## Getting Started

### Setup guide

- MS SQL Server: `Azure SQL Database`, `SQL Server 2016` or greater

#### Network Access

Make sure your SQL Server database can be accessed by Airbyte. If your database is within a VPC, you may need to allow access from the IP you're using to expose Airbyte.

#### **Permissions**

You need a user configured in SQL Server that can create tables and write rows. We highly recommend creating an Airbyte-specific user for this purpose.
In order to allow for normalization, please grant ALTER permissions for the user configured.

#### Target Database

You will need to choose an existing database or create a new database that will be used to store synced data from Airbyte.

### Configuration

You'll need the following information to configure the MSSQL destination:

- **Host**
  - The host name of the MSSQL database.
- **Port**
  - The port of the MSSQL database.
- **Database Name** 
  - The name of the MSSQL database.
- **Default Schema** 
  - The default schema tables are written to if the source does not specify a namespace. The usual value for this field is "public".
- **Username** 
  - The username which is used to access the database.
- **Password** 
  - The password associated with this username.
- **JDBC URL Parameters** 
  - Additional properties to pass to the JDBC URL string when connecting to the database formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3).
- **SSL Method**
  - The SSL configuration supports three modes: Unencrypted, Encrypted \(trust server certificate\), and Encrypted \(verify certificate\).
    - **Unencrypted**: Do not use SSL encryption on the database connection
    - **Encrypted \(trust server certificate\)**: Use SSL encryption without verifying the server's certificate. This is useful for self-signed certificates in testing scenarios, but should not be used in production.
    - **Encrypted \(verify certificate\)**: Use the server's SSL certificate, after standard certificate verification.
      - **Host Name In Certificate** \(optional\): When using certificate verification, this property can be set to specify an expected name for added security. If this value is present, and the server's certificate's host name does not match it, certificate verification will fail.
- **Load Type**
  - The data load type supports two modes:  Insert or Bulk
    - **Insert**: Utilizes SQL `INSERT` statements to load data to the destination table.
    - **Bulk**: Utilizes Azure Blob Storage and the `BULK INSERT` command to load data to the destination table.  If selected, additional configuration is required:
      - **Azure Blob Storage Account Name** - The name of the [Azure Blob Storage account]( https://learn.microsoft.com/azure/storage/blobs/storage-blobs-introduction#storage-accounts).
      - **Azure Blob Storage Container Name** - The name of the [Azure Blob Storage container](https://learn.microsoft.com/azure/storage/blobs/storage-blobs-introduction#containers).
      - **Shared Access Signature** - A [shared access signature (SAS)](https://learn.microsoft.com/azure/storage/common/storage-sas-overview) provides secure delegated access to resources.\
      - **BULK Load Data Source** - Specifies the [external data source name configured in MSSQL](https://learn.microsoft.com/sql/t-sql/statements/bulk-insert-transact-sql), which references the Azure Blob container.
      - **Pre-Load Value Validation** - When enabled, Airbyte will validate all values before loading them into the destination table. This provides stronger data integrity guarantees but may significantly impact performance.

#### MSSQL with Azure Blob Storage (Bulk Upload) Setup Guide

This section describes how to set up and use the **Microsoft SQL Server (MSSQL) connector** with the **Azure Blob Storage Bulk Upload** feature. By staging data in an Azure Blob Storage container and using `BULK INSERT`, you can significantly improve ingestion speed and reduce network overhead for large or frequent data loads.

##### Why Use Azure Blob Storage Bulk Upload?

When handling high data volumes or frequent syncs, row-by-row inserts into MSSQL can become slow and resource-intensive. By staging files in Azure Blob Storage first, you can:
1. **Aggregate Data into Bulk Files**: Data is written to Blob Storage in batches, reducing overhead.
2. **Perform Bulk Ingestion**: MSSQL uses `BULK INSERT` to directly load these files, typically resulting in faster performance compared to conventional row-by-row inserts.

##### Prerequisites

1. **A Microsoft SQL Server Instance**
    - Compatible with on-premises SQL Server or Azure SQL Database.
2. **Azure Blob Storage Account**
    - A storage account and container (e.g., `bulk-staging`) where data files will be placed.
3. **Permissions**
    - **Blob Storage**: ability to create, read, and delete objects within the designated container.
    - **MSSQL**: ability to create or modify tables, and permission to execute `BULK INSERT`.

##### Setup Guide

Follow these steps to configure MSSQL with Azure Blob Storage for bulk uploads.

###### 1. Set Up Azure Blob Storage

1. **Create a Storage Account & Container**
    - In the Azure Portal, create (or reuse) a Storage Account.
    - Within that account, create a container (e.g., `bulk-staging`) for staging your data files.
2. **Establish Access Credentials**
    - Use a **Shared Access Signature (SAS)** scoped to your container.
    - Ensure the SAS token or role assignments include permissions such as **Read**, **Write**, **Delete**, and **List**.

###### 2. Configure MSSQL

See the official [Microsoft documentation](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-external-data-source-transact-sql?view=sql-server-2017&tabs=dedicated#e-create-an-external-data-source-for-bulk-operations-retrieving-data-from-azure-storage) for more details. Below is a simplified overview:

1. **(Optional) Create a Master Encryption Key**  
   If your environment requires a master key to store credentials securely, create one:
   ```sql
   CREATE MASTER KEY ENCRYPTION BY PASSWORD = '<your_password>';
   ```

2. **Create a Database Scoped Credential**  
   Configure a credential that grants MSSQL access to your Blob Storage using the SAS token:
   ```sql
   CREATE DATABASE SCOPED CREDENTIAL <credential_name>
   WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
        SECRET = '<your_sas_token>';
   ```

3. **Create an External Data Source**  
   Point MSSQL to your Blob container using the credential:
   ```sql
   CREATE EXTERNAL DATA SOURCE <data_source_name>
   WITH (
       TYPE = BLOB_STORAGE,
       LOCATION = 'https://<storage_account>.blob.core.windows.net/<container_name>',
       CREDENTIAL = <credential_name>
   );
   ```
   You’ll reference `<data_source_name>` when configuring the connector.

###### 3. Connector Configuration

You’ll need to supply:

1. **MSSQL Connection Details**
    - The server hostname/IP, port, database name, and authentication (username/password).
2. **Bulk Load Data Source**
    - The name of the external data source you created (e.g., `<data_source_name>`).
3. **Azure Storage Account & Container**
    - The name of the storage account and container.
4. **SAS Token**
    - The token that grants Blob Storage access.

See the [Getting Started: Configuration section](#configuration) of this guide for more details on `BULK INSERT` connector configuration.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version    | Date       | Pull Request                                               | Subject                                                                                             |
|:-----------|:-----------|:-----------------------------------------------------------|:----------------------------------------------------------------------------------------------------|
| 2.0.2      | 2025-03-12 | [55720](https://github.com/airbytehq/airbyte/pull/55720)   | Restore definition ID                                                                               |
| 2.0.1      | 2025-03-12 | [55718](https://github.com/airbytehq/airbyte/pull/55718)   | Fix breaking change information in metadata.yaml                                                    |
| 2.0.0      | 2025-03-11 | [55684](https://github.com/airbytehq/airbyte/pull/55684)   | Release 2.0.0                                                                                       |
| 2.0.0.rc13 | 2025-03-07 | [55252](https://github.com/airbytehq/airbyte/pull/55252)   | RC13: Bugfix for OOM on Bulk Load                                                                   |
| 2.0.0.rc12 | 2025-03-05 | [54159](https://github.com/airbytehq/airbyte/pull/54159)   | RC12: Support For Bulk Insert Using Azure Blob Storage                                              |
| 2.0.0.rc11 | 2025-03-04 | [55193](https://github.com/airbytehq/airbyte/pull/55193)   | RC11: Increase decimal precision                                                                    |
| 2.0.0.rc10 | 2025-02-24 | [54648](https://github.com/airbytehq/airbyte/pull/54648)   | RC10: Fix index column names with hyphens                                                           |
| 2.0.0.rc9  | 2025-02-21 | [54197](https://github.com/airbytehq/airbyte/pull/54197)   | RC9: Fix index column names with invalid characters                                                 |
| 2.0.0.rc8  | 2025-02-20 | [54186](https://github.com/airbytehq/airbyte/pull/54186)   | RC8: Fix String support                                                                             |
| 2.0.0.rc7  | 2025-02-11 | [53364](https://github.com/airbytehq/airbyte/pull/53364)   | RC7: Revert deletion change                                                                         |
| 2.0.0.rc6  | 2025-02-11 | [53364](https://github.com/airbytehq/airbyte/pull/53364)   | RC6: Break up deletes into loop to reduce locking                                                   |
| 2.0.0.rc5  | 2025-02-07 | [53236](https://github.com/airbytehq/airbyte/pull/53236)   | RC5: Use rowlock hint                                                                               |
| 2.0.0.rc4  | 2025-02-06 | [53192](https://github.com/airbytehq/airbyte/pull/53192)   | RC4: Fix config, timehandling, performance tweak                                                    |
| 2.0.0.rc3  | 2025-02-04 | [53174](https://github.com/airbytehq/airbyte/pull/53174)   | RC3: Fix metadata.yaml for publish                                                                  |
| 2.0.0.rc2  | 2025-02-04 | [52704](https://github.com/airbytehq/airbyte/pull/52704)   | RC2: Performance improvement                                                                        |
| 2.0.0.rc1  | 2025-01-24 | [52096](https://github.com/airbytehq/airbyte/pull/52096)   | Release candidate                                                                                   |
| 1.0.3      | 2025-01-10 | [51497](https://github.com/airbytehq/airbyte/pull/51497)   | Use a non root base image                                                                           |
| 1.0.2      | 2024-12-18 | [49891](https://github.com/airbytehq/airbyte/pull/49891)   | Use a base image: airbyte/java-connector-base:1.0.0                                                 |
| 1.0.1      | 2024-11-04 | [\#48134](https://github.com/airbytehq/airbyte/pull/48134) | Fix supported sync modes (destination-mssql 1.x.y does not support dedup)                           |
| 1.0.0      | 2024-04-11 | [\#36050](https://github.com/airbytehq/airbyte/pull/36050) | Update to Dv2 Table Format and Remove normalization                                                 |
| 0.2.0      | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                |
| 0.1.25     | 2023-06-21 | [\#27555](https://github.com/airbytehq/airbyte/pull/27555) | Reduce image size                                                                                   |
| 0.1.24     | 2023-06-05 | [\#27034](https://github.com/airbytehq/airbyte/pull/27034) | Internal code change for future development (install normalization packages inside connector)       |
| 0.1.23     | 2023-04-04 | [\#24604](https://github.com/airbytehq/airbyte/pull/24604) | Support for destination checkpointing                                                               |
| 0.1.22     | 2022-10-21 | [\#18275](https://github.com/airbytehq/airbyte/pull/18275) | Upgrade commons-text for CVE 2022-42889                                                             |
| 0.1.20     | 2022-07-14 | [\#14618](https://github.com/airbytehq/airbyte/pull/14618) | Removed additionalProperties: false from JDBC destination connectors                                |
| 0.1.19     | 2022-05-25 | [\#13054](https://github.com/airbytehq/airbyte/pull/13054) | Destination MSSQL: added custom JDBC parameters support.                                            |
| 0.1.18     | 2022-05-17 | [\#12820](https://github.com/airbytehq/airbyte/pull/12820) | Improved 'check' operation performance                                                              |
| 0.1.17     | 2022-04-05 | [\#11729](https://github.com/airbytehq/airbyte/pull/11729) | Bump mina-sshd from 2.7.0 to 2.8.0                                                                  |
| 0.1.15     | 2022-02-25 | [\#10421](https://github.com/airbytehq/airbyte/pull/10421) | Refactor JDBC parameters handling                                                                   |
| 0.1.14     | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                        |
| 0.1.13     | 2021-12-28 | [\#9158](https://github.com/airbytehq/airbyte/pull/9158)   | Update connector fields title/description                                                           |
| 0.1.12     | 2021-12-01 | [\#8371](https://github.com/airbytehq/airbyte/pull/8371)   | Fixed incorrect handling "\n" in ssh key                                                            |
| 0.1.11     | 2021-11-08 | [\#7719](https://github.com/airbytehq/airbyte/pull/7719)   | Improve handling of wide rows by buffering records based on their byte size rather than their count |
| 0.1.10     | 2021-10-11 | [\#6877](https://github.com/airbytehq/airbyte/pull/6877)   | Add `normalization` capability, add `append+deduplication` sync mode                                |
| 0.1.9      | 2021-09-29 | [\#5970](https://github.com/airbytehq/airbyte/pull/5970)   | Add support & test cases for MSSQL Destination via SSH tunnels                                      |
| 0.1.8      | 2021-08-07 | [\#5272](https://github.com/airbytehq/airbyte/pull/5272)   | Add batch method to insert records                                                                  |
| 0.1.7      | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                        |
| 0.1.6      | 2021-06-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer                                                           |
| 0.1.5      | 2021-07-20 | [\#4874](https://github.com/airbytehq/airbyte/pull/4874)   | declare object types correctly in spec                                                              |
| 0.1.4      | 2021-06-17 | [\#3744](https://github.com/airbytehq/airbyte/pull/3744)   | Fix doc/params in specification file                                                                |
| 0.1.3      | 2021-05-28 | [\#3728](https://github.com/airbytehq/airbyte/pull/3973)   | Change dockerfile entrypoint                                                                        |
| 0.1.2      | 2021-05-13 | [\#3367](https://github.com/airbytehq/airbyte/pull/3671)   | Fix handle symbols unicode                                                                          |
| 0.1.1      | 2021-05-11 | [\#3566](https://github.com/airbytehq/airbyte/pull/3195)   | MS SQL Server Destination Release!                                                                  |

</details>
